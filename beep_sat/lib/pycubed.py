"""
CircuitPython driver for PyCubed satellite board

PyCubed mainboard-v04g

* Author(s): Max Holliday

"""
import board, microcontroller
import busio, time, sys
import adafruit_sdcard
from storage import mount,umount,VfsFat
from analogio import AnalogIn
import digitalio

from pycubed_gps import GPS
import pycubed_rfm9x
import bmx160
import adafruit_tsl2561

import neopixel
import bq25883
import adm1176
import ads124s08
from os import listdir, stat, statvfs, mkdir,chdir
from bitflags import bitFlag,multiBitFlag,multiByte
from micropython import const
import sx1280

'''
import builtins
builtins.tasko_logging = True
'''

import tasko

# import adafruit_tsl2561
_ROLLOVER_S  = const(281475) # seconds
_ROLLOVER_MS = const(281474977) # ms
_TIMESCALE   = const(1000000)

# NVM register numbers
_BOOTCNT  = const(0)  #0
# _TIME 1 to 5
_VBUSRST  = const(6)  #1
_STATECNT = const(7)  #2
_ROLLCNT  = const(8)  #3 25
_TOUTS    = const(9)  #4
_GSRSP    = const(10) #5
_ICHRG    = const(11) #6
_XDISC    = const(12) #7
_BCOUNT   = const(13) #8
_DWNLINK  = const(14) #9
_RNGERR   = const(15) #10
_FLAG     = const(16) #11 20
# gyro 17 to 19
# fuel gauge 20
# rad file count 21,22
# range file count 23,24
# gps file count 25,26
# data summary 27 to 36
# gs-rssi 37
# dwnlink count 38
_UHFERRS  = const(39)
# crc 40
# sd fail 50

SEND_BUFF=bytearray(252)
BIT_0 = const(0)
BIT_4 = const(4)
BIT_8 = const(8)

class Satellite:
    # General NVM bytes
    c_boot      = multiBitFlag(register=_BOOTCNT, lowest_bit=BIT_0,num_bits=BIT_8)
    c_vbusrst   = multiBitFlag(register=_VBUSRST, lowest_bit=BIT_0,num_bits=BIT_8)
    c_state_err = multiBitFlag(register=_STATECNT,lowest_bit=BIT_0,num_bits=BIT_8)
    c_gs_resp   = multiBitFlag(register=_GSRSP,   lowest_bit=BIT_0,num_bits=BIT_8)
    c_ichrg     = multiBitFlag(register=_ICHRG,   lowest_bit=BIT_0,num_bits=BIT_8)
    c_uhfcrc    = multiBitFlag(register=_UHFERRS, lowest_bit=BIT_0,num_bits=BIT_8)

    # NVM state error counters
    c_discovery = multiBitFlag(register=_XDISC,  lowest_bit=BIT_4,num_bits=BIT_4)
    c_xlink     = multiBitFlag(register=_XDISC,  lowest_bit=BIT_0,num_bits=BIT_4)
    c_idle      = multiBitFlag(register=_BCOUNT, lowest_bit=BIT_4,num_bits=BIT_4)
    c_beacon    = multiBitFlag(register=_BCOUNT, lowest_bit=BIT_0,num_bits=BIT_4)
    c_rad       = multiBitFlag(register=_DWNLINK,lowest_bit=BIT_4,num_bits=BIT_4)
    c_downlink  = multiBitFlag(register=_DWNLINK,lowest_bit=BIT_0,num_bits=BIT_4)
    c_range     = multiBitFlag(register=_RNGERR, lowest_bit=BIT_4,num_bits=BIT_4)

    # Define NVM flags
    f_lowbatt  = bitFlag(register=_FLAG,bit=0)
    f_solar    = bitFlag(register=_FLAG,bit=1)
    f_gpson    = bitFlag(register=_FLAG,bit=2)
    f_isleader = bitFlag(register=_FLAG,bit=3)
    f_lowbtout = bitFlag(register=_FLAG,bit=4)
    c_mphase   = multiBitFlag(register=_FLAG,lowest_bit=5,num_bits=3)
    f_gpsfix   = bitFlag(register=_RNGERR,bit=0)
    f_shtdwn   = bitFlag(register=_RNGERR,bit=2)

    # data file numbers
    c_radfile   = multiByte(lowest_register=21,num_bytes=2)
    c_rngfile   = multiByte(lowest_register=23,num_bytes=2)
    c_gpsfile   = multiByte(lowest_register=25,num_bytes=2)


    UHF_FREQ = 433 #915.6
    SBAND_FREQ = 2.4
    SCTIME   = bytearray(5)

    def __init__(self):
        """
        Big init routine as the whole board is brought up.
        """
        #Initialize tasko functions
        self.add_task = tasko.add_task
        self.run_later = tasko.run_later
        self.schedule = tasko.schedule
        self.schedule_later = tasko.schedule_later
        self.sleep = tasko.sleep
        self.suspend = tasko.suspend
        self.run= tasko.run

        #Initialize list to store scheduled objects
        self.scheduled_objects=[]

        self.BOOTTIME= const(self.time())
        self.send_buff = memoryview(SEND_BUFF)
        self.debug=True
        self.micro=microcontroller
        self.timeoffset=0
        self.rollover_time = _ROLLOVER_S
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
        self.i2c1  = busio.I2C(board.SCL1,board.SDA1)
        self.i2c2  = busio.I2C(board.SCL2,board.SDA2)
        # self.spi  = busio.SPI(board.SCK,MOSI=board.MOSI,MISO=board.MISO)
        self.spi  = board.SPI()
        self.uart = busio.UART(board.TX,board.RX, baudrate=9600,receiver_buffer_size=512,timeout=5)

        # Define GPS
        self.en_gps = digitalio.DigitalInOut(board.EN_GPS)
        self.en_gps.switch_to_output()

        # Define sdcard
        self._sdcs = digitalio.DigitalInOut(board.SD_CS)
        self._sdcs.switch_to_output(value=True)
        self.filename="/sd/default.txt"
        self.filesize=0
        self.logfile="/sd/log.txt"
        self.datafiles={'rng':'','rad':'','gps':'','rng-t':''}
        self.filenumbers={
                'rng':self.c_rngfile,
                'rad':self.c_radfile,
                'gps':self.c_gpsfile}

        # Define radio
        self._rf_cs1 = digitalio.DigitalInOut(board.RF1_CS)
        self._rf_rst1 = digitalio.DigitalInOut(board.RF1_RST)
        self._rf_busy1 = digitalio.DigitalInOut(board.RF1_IO4)
        self.radio1_DIO1=digitalio.DigitalInOut(board.RF1_IO1)
        self.radio1_DIO1.switch_to_input()
        self._rf_cs1.switch_to_output(value=True)
        self._rf_rst1.switch_to_output(value=True)
        # self._rf_busy1.switch_to_input()
        _rf_cs2 = digitalio.DigitalInOut(board.RF2_CS)
        _rf_rst2 = digitalio.DigitalInOut(board.RF2_RST)
        radio2_DIO0 = digitalio.DigitalInOut(board.RF2_IO1)
        _rf_cs2.switch_to_output(value=True)
        _rf_rst2.switch_to_output(value=True)
        radio2_DIO0.switch_to_input()
        # Define Rad Sensor
        xtb_cs = digitalio.DigitalInOut(board.PB22)
        xtb_DRDY = digitalio.DigitalInOut(board.PA22)
        xtb_cs.switch_to_output(value=True)
        xtb_DRDY.switch_to_input(pull=digitalio.Pull.UP)

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

        # Initialize sdcard
        try:
            _sd   = adafruit_sdcard.SDCard(self.spi, self._sdcs)
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


        # # Initialize radio #1 - S-BAND
        # try:
        #     self.radio1 = sx1280.SX1280(self.spi, _rf_cs1, _rf_rst1, _rf_busy1, self.SBAND_FREQ,debug=False)
        #     self.radio1.sleep()
        #     self.radio1.default_dio=radio1_DIO1
        #     self.radio1.timeout_handler=self.timeout_handler

        #     self.hardware['Radio1'] = True
        # except Exception as e:
        #     if self.debug: print('[ERROR][RADIO 1]',e)

        # Initialize radio #2 - UHF
        try:
            self.radio2 = pycubed_rfm9x.RFM9x(spi=self.spi, cs=self._rf_cs1, reset=self._rf_rst1, frequency=self.UHF_FREQ,code_rate=8,baudrate=1000000)
            self.radio2.enable_crc=True
            self.radio2.crc_errs = self.c_uhfcrc # crc error counter
            self.radio2.sleep()
            self.hardware['Radio2'] = True
        except Exception as e:
            if self.debug: print('[ERROR][RADIO 2]',e)

        # Initialize Power Monitor
        try:
            self.pwr = adm1176.ADM1176(self.i2c1)
            self.pwr.sense_resistor = 1
            self.hardware['PWR'] = True
        except Exception as e:
            if self.debug: print('[ERROR][Power Monitor]',e)
            # pass

        # Initialize IMU
        try:
            self.IMU = bmx160.BMX160_I2C(self.i2c1)
            self.hardware['IMU'] = True
        except Exception as e:
            if self.debug: print('[ERROR][IMU]',e)
            # pass

        # # Initialize GPS
        # try:
        #     self.gps = GPS(self.uart,debug=False) # still powered off!
        #     self.gps.timeout_handler=self.timeout_handler
        #     self.hardware['GPS'] = True
        # except Exception as e:
        #     if self.debug: print('[ERROR][GPS]',e)

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

    # custom timekeeping with 0.001 second ticks
    def time(self):
        return time.monotonic_ns() // _TIMESCALE
    def check_rollover(self):
        if time.monotonic() // _ROLLOVER_S > self.micro.nvm[_ROLLCNT]:
            self.micro.nvm[_ROLLCNT] = (self.micro.nvm[_ROLLCNT]+1) % 255
            self.timeoffset = self.micro.nvm[_ROLLCNT] * _ROLLOVER_MS
            self.rollover_time = (self.micro.nvm[_ROLLCNT]+1) * _ROLLOVER_S
    def scale_time(self,t):
        # t should be units of ms (i.e. time.monotonic_ns() // 1000000)
        self.SCTIME[:]=(t+self.timeoffset).to_bytes(5,'big')
        return self.SCTIME

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
                self._sdcs.value=False
                self.enable_rf.value=False
                time.sleep(3)
            except:
                print('vbus reset error?')
                pass
            self._resetReg.drive_mode=digitalio.DriveMode.PUSH_PULL
            self._resetReg.value=1

    def new_binfile(self,substring):
        '''
        substring something like '/data/DATA_'
        directory is created on the SD!
        int padded with zeros will be appended to the last found file
        '''
        if self.hardware['SDcard']:
            ff=''
            n=0
            name=None
            for i in self.filenumbers:
                if i in substring:
                    name=i
                    if name is   'rad': n=self.c_radfile
                    elif name is 'rng': n=self.c_rngfile
                    elif name is 'gps': n=self.c_gpsfile
                    else: n=self.filenumbers[name]
                    # print('prior file number found:',n)
                    break
            _folder=substring[:substring.rfind('/')+1]
            _file=substring[substring.rfind('/')+1:]
            print('Creating new file in directory: /sd{} with file prefix: {}'.format(_folder,_file))
            try:
                chdir('/sd'+_folder)
            except OSError:
                print('Directory {} not found. Creating...'.format(_folder))
                try:
                    mkdir('/sd'+_folder)
                except:
                    return None
            for i in range(0xFFFF):
                ff='/sd{}{}{:05}.txt'.format(_folder,_file,(n+i)%0xFFFF)
                try:
                    if n is not None:
                        stat(ff)
                except:
                    n=(n+i)%0xFFFF
                    # print('file number is',n)
                    break
            if name is not None:
                self.filenumbers[name]=n
            print('creating file...',ff)
            with open(ff,'ab') as f:
                f.tell()
            chdir('/')
            return ff

    def new_datafile(self,t):
        try:
            if t is 'rng':
                self.datafiles['rng']=self.new_binfile('/rng/r')
                self.c_rngfile = self.filenumbers['rng']
            elif t is 'gps':
                self.datafiles['gps']=self.new_binfile('/gps/gn')
                self.datafiles['rng-t']=self.new_binfile('/gps/rt')
                self.c_gpsfile = self.filenumbers['gps']
            elif t is 'rad':
                self.datafiles['rad']=self.new_binfile('/rad/rd')
                self.c_radfile = self.filenumbers['rad']
        except: pass

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

    def send_file(self,c_size,filename,start=0,stop=None,p=False):
        if p: print('send_file()',filename)
        # self.send_buff=bytearray(c_size)
        try:
            self.filesize=stat(filename)[6]-start
        except Exception as e:
            if p: print('[send file] {} error: {}'.format(filename,e))
            return []
        if stop is not None:
            self.filesize=stop-start
        # number of packets
        buff_end=c_size+2
        self.send_buff[1]=int((self.filesize)/c_size)
        with open(filename,"rb") as f:
            for i in range(self.send_buff[1]):
                f.seek(start+(i*c_size))
                self.send_buff[0]=i+1
                f.readinto(self.send_buff[2:buff_end])
                yield (self.send_buff[0],self.send_buff[1],buff_end)

    def fifo(self,data,item):
        '''
        First-in first-out buffer
        buffer must be a list, size will not change
        preallocation example: data=[bytes([0]*66)]*30
        '''
        del data[0]
        data.append(item)
        if data[0] != 0:
            return False
        else:
            return True

    def start_gps(self):
        try:
            self.gps.start(pin=self.en_gps,baudrate=230400,message_type='binary',message_interval=10)
        except: pass

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
