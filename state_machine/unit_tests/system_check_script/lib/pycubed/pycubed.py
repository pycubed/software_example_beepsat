"""
CircuitPython driver for PyCubed satellite board
PyCubed Mini mainboard-v02 for Pocketqube Mission
* Author(s): Max Holliday, Yashika Batra
"""
import sdcardio
import pycubed_rfm9x
import board
import microcontroller
import busio
import digitalio
import analogio
import storage
import sys
import neopixel
import pwmio
import bmx160
import drv8830
from bitflags import bitFlag, multiBitFlag
from micropython import const
import adafruit_tsl2561

"""
TO DO:
replace all "prints" with logs
"""

# NVM register numbers
# TODO: confirm registers start in MRAM partition & update board build file
_FLAG = const(20)
_DWNLINK = const(4)
_DCOUNT = const(3)
_RSTERRS = const(2)
_BOOTCNT = const(0)
_LOGFAIL = const(5)


class Satellite:
    # Define NVM flags
    f_deploy = bitFlag(register=_FLAG, bit=1)
    f_mdeploy = bitFlag(register=_FLAG, bit=2)
    f_burn1 = bitFlag(register=_FLAG, bit=3)
    f_burn2 = bitFlag(register=_FLAG, bit=4)

    # Define NVM counters
    c_boot = multiBitFlag(register=_BOOTCNT, lowest_bit=0, num_bits=8)
    c_state_err = multiBitFlag(register=_RSTERRS, lowest_bit=4, num_bits=4)
    c_vbus_rst = multiBitFlag(register=_RSTERRS, lowest_bit=0, num_bits=4)
    c_deploy = multiBitFlag(register=_DCOUNT, lowest_bit=0, num_bits=8)
    c_downlink = multiBitFlag(register=_DWNLINK, lowest_bit=0, num_bits=8)
    c_logfail = multiBitFlag(register=_LOGFAIL, lowest_bit=0, num_bits=8)

    # change to 433?
    UHF_FREQ = 433.0

    def __init__(self):
        """ Big init routine as the whole board is brought up. """
        self._stat = {}
        self.BOOTTIME = const(self.timeon)
        self.hardware = {
            'I2C1': False,
            'I2C2': False,
            'I2C3': False,
            'SPI': False,
            'SDcard': False,
            'Neopixel': False,
            'IMU': False,
            'Radio': False,
            # 'GPS': False,
            # 'WDT': False,
            'Sun -Y': False,
            'Sun -Z': False,
            'Sun -X': False,
            'Sun +Y': False,
            'Sun +Z': False,
            'Sun +X': False,
            'Coil X': False,
            'Coil Y': False,
            'Coil Z': False,
            'Burn Wire 1': False,
            'Burn Wire 2': False
        }
        self.micro = microcontroller

        self.data_cache = {}
        self.filenumbers = {}
        self.vlowbatt = 3.5
        self.debug = True

        # Define battery voltage
        self._vbatt = analogio.AnalogIn(board.BATTERY)

        # Define and initialize SPI, I2C, UART
        self.__init_i2c_spi_uart()

        # Define and initialize sdcard
        self.__init_sdcard()

        # Define and initialize neopixel
        self.__init_neopixel()

        # Define and initialize imu
        self.__init_imu()

        # Define and initialize radio
        self.__init_radio()

        # Initialize Sun Sensors
        self.__init_sun_sensors()

        # Initialize H-Bridges
        self.__init_coil_drivers()

        # Initialize burnwires
        self.__init_burnwires()

    def __init_i2c_spi_uart(self):
        try:
            self.i2c1 = busio.I2C(board.SCL1, board.SDA1)
            self.hardware['I2C1'] = True
        except Exception as e:
            print("[ERROR][I2C1]", e)

        try:
            self.i2c2 = busio.I2C(board.SCL2, board.SDA2)
            self.hardware['I2C2'] = True
        except Exception as e:
            print("[ERROR][I2C2]", e)

        try:
            self.i2c3 = busio.I2C(board.SCL3, board.SDA3)
            self.hardware['I2C3'] = True
        except Exception as e:
            print("[ERROR][I2C3]", e)

        try:
            # self.spi = board.SPI()
            self.spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
            self.hardware['SPI'] = True
        except Exception as e:
            print("[ERROR][SPI]", e)

    def __init_sdcard(self):
        self.filename = "/sd/default.txt"
        self.logfile = "/sd/logs/log000.txt"

        # Initialize sdcard
        try:
            self._sd = sdcardio.SDCard(self.spi, board.CS_SD, baudrate=4000000)
            self._vfs = storage.VfsFat(self._sd)
            storage.mount(self._vfs, "/sd")
            sys.path.append("/sd")
            self.hardware['SDcard'] = True
            # self.new_log() # create new log file
        except Exception as e:
            print('[ERROR][SD Card]', e)

    def __init_neopixel(self):
        # Initialize Neopixel
        try:
            self.neopixel = neopixel.NeoPixel(
                board.NEOPIXEL, 1, brightness=0.2, pixel_order=neopixel.GRB)
            self.neopixel[0] = (0, 0, 0)
            self.hardware['Neopixel'] = True
        except Exception as e:
            print('[WARNING][Neopixel]', e)

    def __init_imu(self):
        # Initialize IMU
        try:
            self.IMU = bmx160.BMX160_I2C(self.i2c1, address=0x68)
            self.hardware['IMU'] = True
        except Exception as e:
            print(f'[ERROR][IMU] {e}\n\tMaybe try address=0x68?')

    def __init_radio(self):
        # Define radio
        self._rf_cs = digitalio.DigitalInOut(board.RF_CS)
        self._rf_rst = digitalio.DigitalInOut(board.RF_RST)
        self.radio_DIO0 = digitalio.DigitalInOut(board.RF_IO0)
        self.radio_DIO0.switch_to_input()
        self.radio_DIO1 = digitalio.DigitalInOut(board.RF_IO1)
        self.radio_DIO1.switch_to_input()
        self._rf_cs.switch_to_output(value=True)
        self._rf_rst.switch_to_output(value=True)

        # Initialize radio - UHF
        try:
            self.radio = pycubed_rfm9x.RFM9x(
                self.spi, self._rf_cs, self._rf_rst,
                self.UHF_FREQ, rfm95pw=True)
            self.radio.dio0 = self.radio_DIO0
            self.radio.sleep()
            self.hardware['Radio'] = True
        except Exception as e:
            print('[ERROR][RADIO]', e)

    def __init_sun_sensors(self):
        sun_sensors = []

        try:
            sun_yn = adafruit_tsl2561.TSL2561(self.i2c2, address=0x29)  # -Y
            sun_sensors.append(sun_yn)
            self.hardware['Sun -Y'] = True
        except Exception as e:
            print('[ERROR][Sun Sensor -Y]', e)

        try:
            sun_zn = adafruit_tsl2561.TSL2561(self.i2c2, address=0x39)  # -Z
            sun_sensors.append(sun_zn)
            self.hardware['Sun -Z'] = True
        except Exception as e:
            print('[ERROR][Sun Sensor -Z]', e)

        try:
            sun_xn = adafruit_tsl2561.TSL2561(self.i2c1, address=0x49)  # -X
            sun_sensors.append(sun_xn)
            self.hardware['Sun -X'] = True
        except Exception as e:
            print('[ERROR][Sun Sensor -X]', e)

        try:
            sun_yp = adafruit_tsl2561.TSL2561(self.i2c1, address=0x29)  # +Y
            sun_sensors.append(sun_yp)
            self.hardware['Sun +Y'] = True
        except Exception as e:
            print('[ERROR][Sun Sensor +Y]', e)

        try:
            sun_zp = adafruit_tsl2561.TSL2561(self.i2c1, address=0x39)  # +Z
            sun_sensors.append(sun_zp)
            self.hardware['Sun +Z'] = True
        except Exception as e:
            print('[ERROR][Sun Sensor +Z]', e)

        try:
            sun_xp = adafruit_tsl2561.TSL2561(self.i2c2, address=0x49)  # +X
            sun_sensors.append(sun_xp)
            self.hardware['Sun +X'] = True
        except Exception as e:
            print('[ERROR][Sun Sensor +X]', e)

        for i in sun_sensors:
            i.enabled = False  # set enabled status to False

        self.sun_sensors = sun_sensors

    def __init_coil_drivers(self):
        coils = []

        try:
            # may need to fix i2c addresses
            # schematic says U7 -> 0xC4 and 0xC5 but these are 8 bit
            drv_x = drv8830.DRV8830(self.i2c1, 0x68)  # U6
            coils.append(drv_x)
            self.hardware['Coil X'] = True
        except Exception as e:
            print('[ERROR][H-Bridge U6]', e)

        try:
            # may need to fix i2c addresses
            # schematic says U7 -> 0xD0 and 0xD1 but these are 8 bit
            drv_y = drv8830.DRV8830(self.i2c1, 0x60)  # U8
            coils.append(drv_y)
            self.hardware['Coil Y'] = True
        except Exception as e:
            print('[ERROR][H-Bridge U8]', e)

        try:
            # may need to fix i2c addresses
            # schematic says U7 -> 0xC0 and 0xC1 but these are 8 bit
            drv_z = drv8830.DRV8830(self.i2c1, 0x62)  # U4
            coils.append(drv_z)
            self.hardware['Coil Z'] = True
        except Exception as e:
            print('[ERROR][H-Bridge U4]', e)

        for driver in coils:
            driver.mode = drv8830.COAST
            driver.vout = 0

        self.coils = coils

    def __init_burnwires(self):
        burnwires = []

        try:
            # changed pinout from BURN1 to PA15 (BURN1 did not support PWMOut)
            self.burnwire1 = pwmio.PWMOut(
                microcontroller.pin.PA19, frequency=1000, duty_cycle=0)
            burnwires.append(self.burnwire1)
            self.hardware['Burn Wire 1'] = True
        except Exception as e:
            print('[ERROR][Burn Wire IC1]', e)

        try:
            # changed pinout from BURN2 to PA18 (BURN2 did not support PWMOut)
            self.burnwire2 = pwmio.PWMOut(
                microcontroller.pin.PA18, frequency=1000, duty_cycle=0)
            burnwires.append(self.burnwire2)
            # Initializing Burn Wire 2 hardware as false; no corresponding integrated circuit yet
            self.hardware['Burn Wire 2'] = False
        except Exception as e:
            print('[ERROR][Burn Wire IC1]', e)

        self.burnwires = burnwires

    def reinit(self, dev):
        """
        reinit: reinitialize radio, sd, or IMU based upon contents of dev
        """
        # dev is a string of all lowercase letters,
        dev = dev.lower()

        # reinitialize device based on string dev
        if dev == 'radio':
            self.radio.__init__(
                self.spi, self._rf_cs, self._rf_rst, self.UHF_FREQ)
        elif dev == 'sd':
            self._sd.__init__(self.spi, self._sdcs, baudrate=1000000)
        elif dev == 'imu':
            self.IMU.__init__(self.i2c1)
        else:
            print('Invalid Device? ->', dev)


# initialize Satellite as pocketqube
pocketqube = Satellite()
