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
import time


"""
Interface functions
"""

def acceleration():
    """ return the accelerometer reading from the IMU """
    return _cubesat.IMU.accel

def magnetic():
    """ return the magnetometer reading from the IMU """
    return _cubesat.IMU.mag

def gyro():
    """ return the gyroscope reading from the IMU """
    return _cubesat.IMU.gyro

def temperature_imu():
    """ return the thermometer reading from the IMU """
    return _cubesat.IMU.temperature  # Celsius


def coildriver_vout(driver_index, vset):
    """ Set a given voltage for a given driver """
    if driver_index == "X" or driver_index == "U7":
        _cubesat.drvx.vout(vset)
    elif driver_index == "Y" or driver_index == "U8":
        _cubesat.drvy.vout(vset)
    elif driver_index == "Z" or driver_index == "U9":
        _cubesat.drvz.vout(vset)
    else:
        # TODO: possibly throw an exception?
        print(driver_index, "is not a defined coil driver.")


def lux(sun_sensor_index):
    """ Return the lux reading for a given sun sensor """
    if sun_sensor_index == "-Y":
        return _cubesat.sun_yn.lux
    elif sun_sensor_index == "-Z":
        return _cubesat.sun_zn.lux
    elif sun_sensor_index == "-X":
        return _cubesat.sun_xn.lux
    elif sun_sensor_index == "+Y":
        return _cubesat.sun_yp.lux
    elif sun_sensor_index == "+Z":
        return _cubesat.sun_zp.lux
    elif sun_sensor_index == "+X":
        return _cubesat.sun_xp.lux
    else:
        # TODO: possibly throw an exception?
        print(sun_sensor_index, "is not a defined sun sensor.")


def burn(burn_num='1', dutycycle=0, duration=1):
    """
    initialize with default burn_num = '1' ; burnwire 2 IC is not set up
    Given a burn wire num, a dutycycle, and a burn duration, control
    the voltage of the corresponding burnwire IC
    "dutycycle" tells us the proportion of total voltage we will
    run the IC at (ex. if "dtycycl" = 0.5, we burn at 1.65 volts)
    """
    # BURN1 = -Z,BURN2 = extra burnwire pin, dutycycle ~0.13%
    dtycycl = int((dutycycle / 100) * (0xFFFF))

    # initialize burnwire based on the burn_num passed to the function
    if '1' in burn_num:
        burnwire = _cubesat.burnwire1
    elif '2' in burn_num:
        # because burnwire2 is not set up, will throw HardwareInitException
        burnwire = _cubesat.burnwire2
    else:
        # TODO: throw an exception?
        return False

    RGB(255, 0, 0)  # set RGB to red

    # set the burnwire's dutycycle; begins the burn
    burnwire.duty_cycle = dtycycl
    time.sleep(duration)  # wait for given duration

    # set burnwire's dutycycle back to 0; ends the burn
    burnwire.duty_cycle = 0
    RGB(0, 0, 0)  # set RGB to no color

    _cubesat._deployA = True  # sets deployment variable to true
    burnwire.deinit()  # deinitialize burnwire

    return _cubesat._deployA  # return true


def temperature_cpu():
    """ return the temperature reading from the CPU """
    return _cubesat.micro.cpu.temperature  # Celsius


def RGB(value=None):
    """
    If a value is passed, change current RGB settings to value
    else, return the current RGB settings of the neopixel object
    """
    if value is not None:
        _cubesat.neopixel[0] = value
    return _cubesat.neopixel[0]


def battery_voltage():
    """ return the battery voltage """
    # initialize vbat
    vbat = 0

    for _ in range(50):
        # 65536 = 2^16, number of increments we can have to voltage
        vbat += _cubesat._vbatt.value * 3.3 / 65536

    # 100k/100k voltage divider
    voltage = (vbat / 50) * (100 + 100) / 100

    # volts
    return voltage


def fuel_gauge():
    """ report battery voltage as % full """
    return 100 * battery_voltage() / 4.2


def timeon():
    """ return the time on a monotonic clock """
    return int(time.monotonic())


def reset_boot_count():
    """ reset boot count in non-volatile memory (nvm) """
    _cubesat.c_boot = 0


def incr_logfail_count():
    """ increment logfail count in non-volatile memory (nvm) """
    _cubesat.c_logfail += 1


def reset_logfail_count():
    """ reset logfail count in non-volatile memory (nvm) """
    _cubesat.c_logfail = 0


"""
Define HardwareInitException
"""
class HardwareInitException(Exception):
    pass


"""
Define constants, Satellite attributes and Satellite Class
"""
# NVM register numbers
_FLAG = const(20)
_DWNLINK = const(4)
_DCOUNT = const(3)
_RSTERRS = const(2)
_BOOTCNT = const(0)
_LOGFAIL = const(5)

# Satellite attributes
vlowbatt = 3.0
BOOTTIME = int(time.monotonic())
data_cache = {}

class _Satellite:
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

    UHF_FREQ = 433.0

    instance = None

    def __new__(cls):
        if not cls.instance:
            cls.instance = object.__new__(cls)
            cls.instance = super(_Satellite, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        """ Big init routine as the whole board is brought up. """
        self.hardware = {
            'I2C1': False,
            'I2C2': False,
            'I2C3': False,
            'SPI': False,
            'SDcard': False,
            'Neopixel': False,
            'IMU': False,
            'Radio': False,
            'Sun-Y': False,
            'Sun-Z': False,
            'Sun-X': False,
            'Sun+Y': False,
            'Sun+Z': False,
            'Sun+X': False,
            'CoilDriverX': False,
            'CoilDriverY': False,
            'CoilDriverZ': False,
            'Burnwire1': False,
            'Burnwire2': False,
            'WDT': False  # Watch Dog Timer pending
        }
        self.micro = microcontroller
        self._vbatt = analogio.AnalogIn(board.BATTERY)  # Define battery voltage
        # self._stat = {}  # Do we need this? Only used in logging functions
        # self.filenumbers = {}  # Do we need this? Not used in library
        # self.debug = True  # Do we need this? Not used in library

        # Define and initialize hardware
        self._init_i2c1()
        self._init_i2c2()
        self._init_i2c3()
        self._init_spi()
        self._init_sdcard()
        self._init_neopixel()
        self._init_imu()
        self._init_radio()
        self._init_sun_minusy()
        self._init_sun_minusz()
        self._init_sun_minusx()
        self._init_sun_plusy()
        self._init_sun_plusz()
        self._init_sun_plusx()
        self._init_coildriverx()
        self._init_coildrivery()
        self._init_coildriverz()
        self._init_burnwire1()
        self._init_burnwire2()

    def _init_i2c1(self):
        try:
            self._i2c1 = busio.I2C(board.SCL1, board.SDA1)
            self.hardware['I2C1'] = True
        except Exception as e:
            print("[ERROR][Initializing I2C1]", e)

    def _init_i2c2(self):
        try:
            self._i2c2 = busio.I2C(board.SCL2, board.SDA2)
            self.hardware['I2C2'] = True
        except Exception as e:
            print("[ERROR][Initializing I2C2]", e)

    def _init_i2c3(self):
        try:
            self._i2c3 = busio.I2C(board.SCL3, board.SDA3)
            self.hardware['I2C3'] = True
        except Exception as e:
            print("[ERROR][Initializing I2C3]", e)

    def _init_spi(self):
        """ Define and initialize SPI bus """
        try:
            self._spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
            self.hardware['SPI'] = True
        except Exception as e:
            print("[ERROR][Initializing SPI]", e)

    def _init_sdcard(self):
        """ Define SD Parameters and initialize SD Card """
        try:
            self._sd = sdcardio.SDCard(self.spi, board.CS_SD, baudrate=4000000)
            self._vfs = storage.VfsFat(self.sd)
            storage.mount(self.vfs, "/sd")
            sys.path.append("/sd")
            self.hardware['SDcard'] = True
        except Exception as e:
            print('[ERROR][Initializing SD Card]', e)

    def _init_neopixel(self):
        """ Define neopixel parameters and initialize """
        try:
            self._neopixel = neopixel.NeoPixel(
                board.NEOPIXEL, 1, brightness=0.2, pixel_order=neopixel.GRB)
            self.neopixel[0] = (0, 0, 0)
            self.hardware['Neopixel'] = True
        except Exception as e:
            print('[WARNING][Initializing Neopixel]', e)

    def _init_imu(self):
        """ Define IMU parameters and initialize """
        try:
            self._imu = bmx160.BMX160_I2C(self.i2c1, address=0x68)
            self.hardware['IMU'] = True
        except Exception as e:
            print(f'[ERROR][Initializing IMU] {e}\n\tMaybe try address=0x68?')

    def _init_radio(self):
        """ Define radio parameters and initialize UHF radio """
        self._rf_cs = digitalio.DigitalInOut(board.RF_CS)
        self._rf_rst = digitalio.DigitalInOut(board.RF_RST)
        self.radio_DIO0 = digitalio.DigitalInOut(board.RF_IO0)
        self.radio_DIO0.switch_to_input()
        self.radio_DIO1 = digitalio.DigitalInOut(board.RF_IO1)
        self.radio_DIO1.switch_to_input()
        self._rf_cs.switch_to_output(value=True)
        self._rf_rst.switch_to_output(value=True)

        try:
            self._radio = pycubed_rfm9x.RFM9x(
                self.spi, self._rf_cs, self._rf_rst,
                self.UHF_FREQ, rfm95pw=True)
            self.radio.dio0 = self.radio_DIO0
            self.radio.sleep()
            self.hardware['Radio'] = True
        except Exception as e:
            print('[ERROR][Initializing RADIO]', e)

    def _init_sun_minusy(self):
        # TODO: check sun sensor addresses on the schematic once
        try:
            self._sun_yn = adafruit_tsl2561.TSL2561(self.i2c2, address=0x29)  # -Y
            self.sun_yn.enabled = False
            self.hardware['Sun-Y'] = True
        except Exception as e:
            print('[ERROR][Initializing Sun Sensor -Y]', e)

    def _init_sun_minusz(self):
        # TODO: check sun sensor addresses on the schematic once
        try:
            self._sun_zn = adafruit_tsl2561.TSL2561(self.i2c2, address=0x39)  # -Z
            self.sun_zn.enabled = False
            self.hardware['Sun-Z'] = True
        except Exception as e:
            print('[ERROR][Initializing Sun Sensor -Z]', e)

    def _init_sun_minusx(self):
        # TODO: check sun sensor addresses on the schematic once
        try:
            self._sun_xn = adafruit_tsl2561.TSL2561(self.i2c1, address=0x49)  # -X
            self.sun_xn.enabled = False
            self.hardware['Sun-X'] = True
        except Exception as e:
            print('[ERROR][Initializing Sun Sensor -X]', e)

    def _init_sun_plusy(self):
        # TODO: check sun sensor addresses on the schematic once
        try:
            self._sun_yp = adafruit_tsl2561.TSL2561(self.i2c1, address=0x29)  # +Y
            self.sun_yp.enabled = False
            self.hardware['Sun+Y'] = True
        except Exception as e:
            print('[ERROR][Initializing Sun Sensor +Y]', e)

    def _init_sun_plusz(self):
        # TODO: check sun sensor addresses on the schematic once
        try:
            self._sun_zp = adafruit_tsl2561.TSL2561(self.i2c1, address=0x39)  # +Z
            self.sun_zp.enabled = False
            self.hardware['Sun+Z'] = True
        except Exception as e:
            print('[ERROR][Initializing Sun Sensor +Z]', e)

    def _init_sun_plusx(self):
        # TODO: check sun sensor addresses on the schematic once
        try:
            self._sun_xp = adafruit_tsl2561.TSL2561(self.i2c2, address=0x49)  # +X
            self.sun_xp.enabled = False
            self.hardware['Sun+X'] = True
        except Exception as e:
            print('[ERROR][Initializing Sun Sensor +X]', e)

    def _init_coildriverx(self):
        # TODO: check coil driver addresses on the schematic once
        try:
            # may need to fix i2c addresses
            # schematic says U7 -> 0xC4 and 0xC5 but these vals are 8 bit instead of 7
            self._drv_x = drv8830.DRV8830(self.i2c1, 0x68)  # U7
            self.drv_x.mode = drv8830.COAST
            self.drv_x.vout = 0
            self.hardware['CoilDriverX'] = True
        except Exception as e:
            print('[ERROR][Initializing H-Bridge U7]', e)

    def _init_coildrivery(self):
        # TODO: check coil driver addresses on the schematic once
        try:
            # may need to fix i2c addresses
            # schematic says U8 -> 0xD0 and 0xD1 but these vals are 8 bit instead of 7
            self._drv_y = drv8830.DRV8830(self.i2c1, 0x60)  # U8
            self.drv_y.mode = drv8830.COAST
            self.drv_y.vout = 0
            self.hardware['CoilDriverY'] = True
        except Exception as e:
            print('[ERROR][Initializing H-Bridge U8]', e)

    def _init_coildriverz(self):
        # TODO: check coil driver addresses on the schematic once
        try:
            # may need to fix i2c addresses
            # schematic says U9 -> 0xC0 and 0xC1 but these vals are 8 bit instead of 7
            self._drv_z = drv8830.DRV8830(self.i2c1, 0x62)  # U9
            self.drv_z.mode = drv8830.COAST
            self.drv_z.vout = 0
            self.hardware['CoilDriverZ'] = True
        except Exception as e:
            print('[ERROR][Initializing H-Bridge U9]', e)

    def _init_burnwire1(self):
        # TODO: update firmware so we can use board.BURN1 and board.BURN2
        # instead of microcontroller.pin.PA19 and microcontroller.pin.PA18
        try:
            # changed pinout from BURN1 to PA19 (BURN1 did not support PWMOut)
            self._burnwire1 = pwmio.PWMOut(
                microcontroller.pin.PA19, frequency=1000, duty_cycle=0)
            self.hardware['Burnwire1'] = True
        except Exception as e:
            print('[ERROR][Initializing Burn Wire IC1]', e)

    def _init_burnwire2(self):
        # TODO: update firmware so we can use board.BURN1 and board.BURN2
        # instead of microcontroller.pin.PA19 and microcontroller.pin.PA18
        try:
            # changed pinout from BURN2 to PA18 (BURN2 did not support PWMOut)
            self._burnwire2 = pwmio.PWMOut(
                microcontroller.pin.PA18, frequency=1000, duty_cycle=0)
            # Initializing Burn Wire 2 hardware as false; no corresponding IC yet
            self.hardware['Burnwire2'] = False
        except Exception as e:
            print('[ERROR][Initializing Burn Wire IC2]', e)

    def reinit(self, device_string):
        """ Reinit: reinitialize radio, sd, or IMU based upon contents of dev """
        # dev is a string of all lowercase letters,
        dev = device_string.lower()

        if dev == "i2c1":
            self._init_i2c1()
        elif dev == "i2c2":
            self._init_i2c2()
        elif dev == "i2c3":
            self._init_i2c3()
        elif dev == "spi":
            self._init_spi()
        elif dev == "sd":
            self._init_sdcard()
        elif dev == "neopixel":
            self._init_neopixel()
        elif dev == "imu":
            self._init_imu()
        elif dev == "radio":
            self._init_radio()
        elif dev == "sun-y":
            self._init_sun_minusy()
        elif dev == "sun-z":
            self._init_sun_minusz()
        elif dev == "sun-x":
            self._init_sun_minusx()
        elif dev == "sun+y":
            self._init_sun_plusy()
        elif dev == "sun+z":
            self._init_sun_plusz()
        elif dev == "sun+x":
            self._init_sun_plusx()
        elif dev == "coildriverx":
            self._init_coildriverx()
        elif dev == "coildrivery":
            self._init_coildrivery()
        elif dev == "coildriverz":
            self._init_coildriverz()
        elif dev == "burnwire1":
            self._init_burnwire1()
        elif dev == "burnwire2":
            self._init_burnwire2()
        else:
            print("Invalid Device:", device_string)

    def hardwarecheck_device(self, devicestr, device):
        if device is not None:
            return device
        else:
            self.reinit(devicestr)
            if device is None:
                raise HardwareInitException
            else:
                return device

    @property
    def i2c1(self):
        return self.hardwarecheck_device("I2C1", self._i2c1)

    @property
    def i2c2(self):
        return self.hardwarecheck_device("I2C2", self._i2c2)

    @property
    def i2c3(self):
        return self.hardwarecheck_device("I2C3", self._i2c3)

    @property
    def spi(self):
        return self.hardwarecheck_device("SPI", self._spi)

    @property
    def sd(self):
        return self.hardwarecheck_device("SD", self._sd)

    @property
    def neopixel(self):
        return self.hardwarecheck_device("Neopixel", self._neopixel)

    @property
    def imu(self):
        return self.hardwarecheck_device("IMU", self._imu)

    @property
    def radio(self):
        return self.hardwarecheck_device("Radio", self._radio)

    @property
    def sun_yn(self):
        return self.hardwarecheck_device("Sun-Y", self._sun_yn)

    @property
    def sun_zn(self):
        return self.hardwarecheck_device("Sun-Z", self._sun_zn)

    @property
    def sun_xn(self):
        return self.hardwarecheck_device("Sun-X", self._sun_xn)

    @property
    def sun_yp(self):
        return self.hardwarecheck_device("Sun+Y", self._sun_yp)

    @property
    def sun_zp(self):
        return self.hardwarecheck_device("Sun+Z", self._sun_zp)

    @property
    def sun_xp(self):
        return self.hardwarecheck_device("Sun+X", self._sun_xp)

    @property
    def drv_x(self):
        return self.hardwarecheck_device("CoilDriverX", self._drv_x)

    @property
    def drv_y(self):
        return self.hardwarecheck_device("CoilDriverY", self._drv_y)

    @property
    def drv_z(self):
        return self.hardwarecheck_device("CoilDriverZ", self._drv_z)

    @property
    def burnwire1(self):
        return self.hardwarecheck_device("Burnwire1", self._burnwire1)

    @property
    def burnwire2(self):
        return self.hardwarecheck_device("Burnwire2", self._burnwire2)


# initialize Satellite as cubesat
_cubesat = _Satellite()

# Make radio accesible
radio = _cubesat.radio
cubesat_microcontroller = _cubesat.micro
