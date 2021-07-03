"""
CircuitPython driver for PyCubed satellite board

PyCubed mainboard-v5
CircuitPython version 7.0 alpha

* Author(s): Max Holliday

"""
import board, microcontroller
import busio, time, sys
from storage import mount,umount,VfsFat
from analogio import AnalogIn
import digitalio, sdcardio, tasko

import pycubed_rfm9x # Radio
import bmx160 # IMU

import neopixel # RGB LED
import bq25883 # USB charger
import adm1176 # power monitor
from os import listdir,stat,statvfs,mkdir,chdir
from bitflags import bitFlag,multiBitFlag,multiByte
from micropython import const


# NVM register numbers
_BOOTCNT  = const(0)  #0
_VBUSRST  = const(6)  #1
_STATECNT = const(7)  #2
_TOUTS    = const(9)  #4
_GSRSP    = const(10) #5
_ICHRG    = const(11) #6
_FLAG     = const(16) #11 20

BIT_0 = const(0)
BIT_4 = const(4)
BIT_8 = const(8)

SEND_BUFF=bytearray(252)

class Satellite:
    # General NVM counters
    c_boot      = multiBitFlag(register=_BOOTCNT, lowest_bit=BIT_0,num_bits=BIT_8)
    c_vbusrst   = multiBitFlag(register=_VBUSRST, lowest_bit=BIT_0,num_bits=BIT_8)
    c_state_err = multiBitFlag(register=_STATECNT,lowest_bit=BIT_0,num_bits=BIT_8)
    c_gs_resp   = multiBitFlag(register=_GSRSP,   lowest_bit=BIT_0,num_bits=BIT_8)
    c_ichrg     = multiBitFlag(register=_ICHRG,   lowest_bit=BIT_0,num_bits=BIT_8)

    # Define NVM flags
    f_lowbatt  = bitFlag(register=_FLAG,bit=0)
    f_solar    = bitFlag(register=_FLAG,bit=1)
    f_gpson    = bitFlag(register=_FLAG,bit=2)
    f_lowbtout = bitFlag(register=_FLAG,bit=3)
    f_gpsfix   = bitFlag(register=_FLAG,bit=4)
    f_shtdwn   = bitFlag(register=_FLAG,bit=5)

    def __init__(self):
        """
        Big init routine as the whole board is brought up.
        """
        # create asyncio object
        self.tasko=tasko

        # Dict to store scheduled objects by name
        self.scheduled_tasks={}

        self.data_cache={}
        self.vlowbatt=6.0

        self.BOOTTIME= const(time.time())
        self.send_buff = memoryview(SEND_BUFF)
        self.debug=True
        self.micro=microcontroller
        self.hardware = {
                       'IMU':    False,
                       'Radio1': False,
                       'Radio2': False,
                       'SDcard': False,
                       'GPS':    False,
                       'WDT':    False,
                       'USB':    False,
                       'PWR':    False,
                       'Sun':    False,
                       'XTB':    False}
        # Define burn wires:
        self._relayA = digitalio.DigitalInOut(board.RELAY_A)
        self._relayA.switch_to_output(drive_mode=digitalio.DriveMode.OPEN_DRAIN)
        self._resetReg = digitalio.DigitalInOut(board.VBUS_RST)
        self._resetReg.switch_to_output(drive_mode=digitalio.DriveMode.OPEN_DRAIN)

        # Define battery voltage
        self._vbatt = AnalogIn(board.BATTERY)

        # Define MPPT charge current measurement
        self._ichrg = AnalogIn(board.L1PROG)
        self._chrg = digitalio.DigitalInOut(board.CHRG)
        self._chrg.switch_to_input()

        # Define SPI,I2C,UART
        self.i2c1  = busio.I2C(board.SCL,board.SDA)
        self.spi   = board.SPI()
        self.uart  = busio.UART(board.TX,board.RX)

        # Define GPS
        self.en_gps = digitalio.DigitalInOut(board.EN_GPS)
        self.en_gps.switch_to_output()

        # Define filesystem stuff
        self.logfile="/log.txt"

        # Define radio
        _rf_cs1 = digitalio.DigitalInOut(board.RF1_CS)
        _rf_rst1 = digitalio.DigitalInOut(board.RF1_RST)
        self.enable_rf = digitalio.DigitalInOut(board.EN_RF)
        self.radio1_DIO0=digitalio.DigitalInOut(board.RF1_IO0)
        self.enable_rf.switch_to_output(value=True)
        _rf_cs1.switch_to_output(value=True)
        _rf_rst1.switch_to_output(value=True)
        self.radio1_DIO0.switch_to_input()

        # Initialize sdcard (always init SD before anything else on spi bus)
        try:
            _sd = sdcardio.SDCard(self.spi, board.SD_CS, baudrate=4000000)
            _vfs = VfsFat(_sd)
            mount(_vfs, "/sd")
            self.fs=_vfs
            sys.path.append("/sd")
            self.hardware['SDcard'] = True
        except Exception as e:
            if self.debug: print('[ERROR][SD Card]',e)

        # Initialize Neopixel
        try:
            self.neopixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2, pixel_order=neopixel.GRBW)
            self.neopixel[0] = (0,0,0)
            self.hardware['Neopixel'] = True
        except Exception as e:
            if self.debug: print('[WARNING][Neopixel]',e)

        # Initialize USB charger
        try:
            self.usb = bq25883.BQ25883(self.i2c1)
            self.usb.charging = False
            self.usb.wdt = False
            self.usb.led=False
            # TODO: check ILIM registers
            self.usb.charging_current=8 #400mA
            self.usb_charging=False
            self.hardware['USB'] = True
        except Exception as e:
            if self.debug: print('[ERROR][USB Charger]',e)

        # Initialize Power Monitor
        try:
            self.pwr = adm1176.ADM1176(self.i2c1)
            self.pwr.sense_resistor = 0.1
            self.hardware['PWR'] = True
        except Exception as e:
            if self.debug: print('[ERROR][Power Monitor]',e)

        # Initialize IMU
        try:
            self.IMU = bmx160.BMX160_I2C(self.i2c1)
            self.hardware['IMU'] = True
        except Exception as e:
            if self.debug: print('[ERROR][IMU]',e)

        # # Initialize GPS
        # try:
        #     self.gps = GPS(self.uart,debug=False) # still powered off!
        #     self.gps.timeout_handler=self.timeout_handler
        #     self.hardware['GPS'] = True
        # except Exception as e:
        #     if self.debug: print('[ERROR][GPS]',e)

        # Initialize radio #1 - UHF
        try:
            self.radio1 = pycubed_rfm9x.RFM9x(self.spi, _rf_cs1, _rf_rst1,
                433.0,code_rate=8,baudrate=1320000)
            self.radio1.dio0=self.radio1_DIO0
            self.radio1.enable_crc=True
            self.radio1.tx_power=13
            self.radio1.sleep()
            self.hardware['Radio1'] = True
        except Exception as e:
            if self.debug: print('[ERROR][RADIO 1]',e)

    def reinit(self,dev):
        dev=dev.lower()
        if   dev=='gps':
            self.gps.__init__(self.uart,debug=False)
        elif dev=='pwr':
            self.pwr.__init__(self.i2c1)
        elif dev=='usb':
            self.usb.__init__(self.i2c1)
        elif dev=='imu':
            self.IMU.__init__(self.i2c1)
        else:
            print('Invalid Device? ->',dev)

    @property
    def acceleration(self):
        if self.hardware['IMU']:
            return self.IMU.accel

    @property
    def magnetic(self):
        if self.hardware['IMU']:
            return self.IMU.mag

    @property
    def gyro(self):
        if self.hardware['IMU']:
            return self.IMU.gyro

    @property
    def temperature(self):
        if self.hardware['IMU']:
            return self.IMU.temperature # Celsius

    @property
    def RGB(self):
        return self.neopixel[0]
    @RGB.setter
    def RGB(self,value):
        if self.hardware['Neopixel']:
            try:
                self.neopixel[0] = value
            except Exception as e:
                print('[WARNING]',e)

    @property
    def charge_batteries(self):
        if self.hardware['USB']:
            return self.usb_charging
    @charge_batteries.setter
    def charge_batteries(self,value):
        if self.hardware['USB']:
            self.usb_charging=value
            self.usb.led=value
            self.usb.charging=value

    @property
    def battery_voltage(self):
        vbat=0
        for _ in range(50):
            vbat+=self._vbatt.value * 3.3 / 65536
        _voltage = (vbat/50)*(316+110)/110 # 316/110 voltage divider
        return _voltage # volts

    def fuel_gauge(self):
        '''
        report battery voltage as % full
        min=7.1 max=8.4 difference=1.3
        '''
        return round(100*(self.battery_voltage-7.2)/1.2)

    @property
    def system_voltage(self):
        if self.hardware['PWR']:
            try:
                return self.pwr.read()[0] # volts
            except Exception as e:
                print('[WARNING][PWR Monitor]',e)
        else:
            print('[WARNING] Power monitor not initialized')

    @property
    def current_draw(self):
        if self.hardware['PWR']:
            cnt=0
            idraw=0
            for i in range(50): # average 50 readings
                # print(i)
                try:
                    idraw+=self.pwr.read()[1]
                except Exception as e:
                    print('[WARNING][PWR Monitor]',e)
                    continue
            return (idraw/50)*1000 # mA
        else:
            print('[WARNING] Power monitor not initialized')

    def charge_current(self,raw=False):
        _charge = self._ichrg.value * 3.3 / 65536
        _charge = ((_charge*988)/3010)*1000
        if raw:
            return round(_charge/2) % 255
        return _charge # mA

    @property
    def solar_charging(self):
        return not self._chrg.value

    @property
    def reset_vbus(self):
        self.micro.nvm[_VBUSRST]+=1

        # if we've reset vbus 255 times, something is wrong
        if self.micro.nvm[_VBUSRST] < 254:
            try:
                umount('/sd')
                self.spi.deinit()
                self.enable_rf.value=False
                time.sleep(3)
            except Exception as e:
                print('vbus reset error?', e)
                pass
            self._resetReg.drive_mode=digitalio.DriveMode.PUSH_PULL
            self._resetReg.value=1

    def log(self, msg):
        if self.hardware['SDcard']:
            with open(self.logfile, "a+") as f:
                t=int(time.monotonic())
                f.write('{}, {}\n'.format(t,msg))

    def print_file(self,filedir=None,binary=False):
        if filedir==None:
            return
        print('\n--- Printing File: {} ---'.format(filedir))
        if binary:
            with open(filedir, "rb") as file:
                print(file.read())
                print('')
        else:
            with open(filedir, "r") as file:
                for line in file:
                    print(line.strip())

    def timeout_handler(self):
        print('Incrementing timeout register')
        if (self.micro.nvm[_TOUTS] + 1) >= 255:
            self.micro.nvm[_TOUTS]=0
            # soft reset
            self.micro.on_next_reset(self.micro.RunMode.NORMAL)
            self.micro.reset()
        else:
            self.micro.nvm[_TOUTS] += 1


cubesat = Satellite()
