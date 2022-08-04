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
from ulab.numpy import array

class hardware:
    """Modified @hardware decorator.
    Based on the code from: https://docs.python.org/3/howto/descriptor.html#properties
    Attempts to return the appropriate hardware device.
    If this fails, it will attempt to reinitialize the hardware.
    If this fails again, it will raise an exception.
    """

    def __init__(self, fget=None):
        self.fget = fget

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError(f'unreadable attribute {self._name}')

        device, reinit = self.fget(obj)

        if device is not None:
            return device
        else:
            reinit()
            device, _ = self.fget(obj)
            if device is None:
                raise HardwareInitException
            else:
                return device


"""
IMU Interface functions
"""
def acceleration():
    """ return the accelerometer reading from the IMU in m/s^2 """
    return _cubesat.imu.accel


def magnetic():
    """ return the magnetometer reading from the IMU in µT """
    return _cubesat.imu.mag


def gyro():
    """ return the gyroscope reading from the IMU in deg/s """
    return _cubesat.imu.gyro


def temperature_imu():
    """ return the thermometer reading from the IMU in celsius """
    return _cubesat.imu.temperature


"""
Coil Driver Interface functions
"""
def coildriver_vout(driver_index, projected_voltage):
    """ Set a given voltage for a given coil driver """
    if driver_index == "X" or driver_index == "U7":
        _cubesat.drv_x.throttle_volts = projected_voltage
    elif driver_index == "Y" or driver_index == "U8":
        _cubesat.drv_y.throttle_volts = projected_voltage
    elif driver_index == "Z" or driver_index == "U9":
        _cubesat.drv_z.throttle_volts = projected_voltage
    else:
        print(driver_index, "is not a defined coil driver")
        return


"""
Sun Sensor Interface functions
"""
def sun_vector():
    """Returns the sun pointing vector in the body frame"""
    return array(
        [_cubesat.sun_xp.lux - _cubesat.sun_xn.lux,
         _cubesat.sun_yp.lux - _cubesat.sun_yn.lux,
         _cubesat.sun_zp.lux - _cubesat.sun_zn.lux])


"""
Burnwire Interface functions
"""
def burn(burn_num='1', dutycycle=0, duration=1):
    """
    Given a burn wire num, a dutycycle, and a burn duration, control
    the voltage of the corresponding burnwire IC
    "dutycycle" tells us the proportion of total voltage we will
    run the IC at (ex. if "dtycycl" = 0.5, we burn at 1.65 volts)

    initialize with default burn_num = '1' ; burnwire 2 IC is not set up
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
        print("Burnwire2 IC is not set up.")
        return False

    setRGB(255, 0, 0)  # set RGB to red

    # set the burnwire's dutycycle; begins the burn
    burnwire.duty_cycle = dtycycl
    time.sleep(duration)  # wait for given duration

    # set burnwire's dutycycle back to 0; ends the burn
    burnwire.duty_cycle = 0
    setRGB(0, 0, 0)  # set RGB to no color

    _cubesat._deployA = True  # sets deployment variable to true
    burnwire.deinit()  # deinitialize burnwire

    return _cubesat._deployA  # return true


"""
Miscellaneous Interface functions
"""
def temperature_cpu():
    """ return the temperature reading from the CPU in celsius """
    return _cubesat.micro.cpu.temperature

def setRGB(v):
    _cubesat.neopixel[0] = v

def getRGB():
    return _cubesat.neopixel[0]

def battery_voltage():
    """
    Return the battery voltage
    _cubesat._vbatt.value converts the analog value of the
    board.BATTERY pin to a digital one. We read this value 50
    times and then later average it to get as close as possible
    to a reliable battery voltage value
    """
    # initialize vbat
    vbat = 0

    # get the battery value 50 times
    for _ in range(50):
        # 65536 = 2^16, number of increments we can have to voltage
        vbat += _cubesat._vbatt.value * 3.3 / 65536

    # vbat / 50 = average of all battery voltage values read
    # 100k/100k voltage divider
    voltage = (vbat / 50) * (100 + 100) / 100

    # volts
    return voltage


def timeon():
    """ return the time on a monotonic clock """
    return int(time.monotonic()) - _cubesat.BOOTTIME


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

    # Set hardware attributes to None
    # Needed for things not to crash
    _i2c1, _i2c2, _i2c3, _spi, _sd, _neopixel = None, None, None, None, None, None
    _imu, _radio, _sun_yn, _sun_zn, _sun_xn = None, None, None, None, None
    _sun_yp, _sun_zp, _sun_xp, _drv_x, _drv_y = None, None, None, None, None
    _drv_z, _burnwire1, _burnwire2 = None, None, None

    UHF_FREQ = 433.0

    instance = None

    def __new__(cls):
        """
        Override the built-in __new__ function
        Ensure only one instance of this class can be made per process
        """
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
        self.BOOTTIME = int(time.monotonic())  # get monotonic time at initialization
        self.micro = microcontroller
        self._vbatt = analogio.AnalogIn(board.BATTERY)  # Battery voltage

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
        """ Initialize I2C1 bus """
        try:
            self._i2c1 = busio.I2C(board.SCL1, board.SDA1)
            self.hardware['I2C1'] = True
        except Exception as e:
            print("[ERROR][Initializing I2C1]", e)

    def _init_i2c2(self):
        """ Initialize I2C2 bus """
        try:
            self._i2c2 = busio.I2C(board.SCL2, board.SDA2)
            self.hardware['I2C2'] = True
        except Exception as e:
            print("[ERROR][Initializing I2C2]", e)

    def _init_i2c3(self):
        """ Initialize I2C3 bus """
        try:
            self._i2c3 = busio.I2C(board.SCL3, board.SDA3)
            self.hardware['I2C3'] = True
        except Exception as e:
            print("[ERROR][Initializing I2C3]", e)

    def _init_spi(self):
        """ Initialize SPI bus """
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
            storage.mount(self._vfs, "/sd")
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
            print('[ERROR][Initializing Neopixel]', e)

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
        """ Initialize the -Y sun sensor on I2C2 """
        try:
            self._sun_yn = adafruit_tsl2561.TSL2561(self.i2c2, address=0x29)
            self.sun_yn.enabled = False
            self.hardware['Sun-Y'] = True
        except Exception as e:
            print('[ERROR][Initializing Sun Sensor -Y]', e)

    def _init_sun_minusz(self):
        """ Initialize the -Z sun sensor on I2C2 """
        try:
            self._sun_zn = adafruit_tsl2561.TSL2561(self.i2c2, address=0x39)
            self.sun_zn.enabled = False
            self.hardware['Sun-Z'] = True
        except Exception as e:
            print('[ERROR][Initializing Sun Sensor -Z]', e)

    def _init_sun_minusx(self):
        """ Initialize the -X sun sensor on I2C1 """
        try:
            self._sun_xn = adafruit_tsl2561.TSL2561(self.i2c1, address=0x49)
            self.sun_xn.enabled = False
            self.hardware['Sun-X'] = True
        except Exception as e:
            print('[ERROR][Initializing Sun Sensor -X]', e)

    def _init_sun_plusy(self):
        """ Initialize the +Y sun sensor on I2C1 """
        try:
            self._sun_yp = adafruit_tsl2561.TSL2561(self.i2c1, address=0x29)
            self.sun_yp.enabled = False
            self.hardware['Sun+Y'] = True
        except Exception as e:
            print('[ERROR][Initializing Sun Sensor +Y]', e)

    def _init_sun_plusz(self):
        """ Initialize the +Z sun sensor on I2C1 """
        try:
            self._sun_zp = adafruit_tsl2561.TSL2561(self.i2c1, address=0x39)
            self.sun_zp.enabled = False
            self.hardware['Sun+Z'] = True
        except Exception as e:
            print('[ERROR][Initializing Sun Sensor +Z]', e)

    def _init_sun_plusx(self):
        """ Initialize the +X sun sensor on I2C2 """
        try:
            self._sun_xp = adafruit_tsl2561.TSL2561(self.i2c2, address=0x49)
            self.sun_xp.enabled = False
            self.hardware['Sun+X'] = True
        except Exception as e:
            print('[ERROR][Initializing Sun Sensor +X]', e)

    def _init_coildriverx(self):
        """ Initialize Coil Driver X on I2C3, set mode and voltage """
        try:
            self._drv_x = drv8830.DRV8830(self.i2c3, 0x62)  # U7
            self.hardware['CoilDriverX'] = True
        except Exception as e:
            print('[ERROR][Initializing H-Bridge U7]', e)

    def _init_coildrivery(self):
        """ Initialize Coil Driver Y on I2C3, set mode and voltage """
        try:
            self._drv_y = drv8830.DRV8830(self.i2c3, 0x68)  # U8
            self.hardware['CoilDriverY'] = True
        except Exception as e:
            print('[ERROR][Initializing H-Bridge U8]', e)

    def _init_coildriverz(self):
        """ Initialize Coil Driver Z on I2C3, set mode and voltage """
        try:
            self._drv_z = drv8830.DRV8830(self.i2c3, 0x60)  # U9
            self.hardware['CoilDriverZ'] = True
        except Exception as e:
            print('[ERROR][Initializing H-Bridge U9]', e)

    def _init_burnwire1(self):
        """ Initialize Burnwire1 on PA19 """
        # TODO: update firmware so we can use board.BURN1
        try:
            # changed pinout from BURN1 to PA19 (BURN1 did not support PWMOut)
            self._burnwire1 = pwmio.PWMOut(
                microcontroller.pin.PA19, frequency=1000, duty_cycle=0)
            self.hardware['Burnwire1'] = True
        except Exception as e:
            print('[ERROR][Initializing Burn Wire IC1]', e)

    def _init_burnwire2(self):
        """ Initialize Burnwire2 on PA18 """
        # TODO: update firmware so we can use board.BURN2
        try:
            # changed pinout from BURN2 to PA18 (BURN2 did not support PWMOut)
            self._burnwire2 = pwmio.PWMOut(
                microcontroller.pin.PA18, frequency=1000, duty_cycle=0)
            # Initializing Burn Wire 2 hardware as false; no corresponding IC
            self.hardware['Burnwire2'] = False
        except Exception as e:
            print('[ERROR][Initializing Burn Wire IC2]', e)

    @hardware
    def i2c1(self):
        """ Return I2C1 bus and init function"""
        return self._i2c1, self._init_i2c1

    @hardware
    def i2c2(self):
        """ Return I2C2 bus object and init function"""
        return self._i2c2, self._init_i2c2

    @hardware
    def i2c3(self):
        """ Return I2C3 bus object and init function"""
        return self._i2c3, self._init_i2c3

    @hardware
    def spi(self):
        """ Return SPI bus object and init function"""
        return self._spi, self._init_i2c3

    @hardware
    def sd(self):
        """ Return SD Card object and init function"""
        return self._sd, self._init_i2c3

    @hardware
    def neopixel(self):
        """Return neopixel and its init function"""
        return self._neopixel, self._init_neopixel

    @hardware
    def imu(self):
        """ Return IMU object and init function"""
        return self._imu, self._init_imu

    @hardware
    def radio(self):
        """ Return Radio and init function"""
        return self._radio, self._init_radio

    @hardware
    def sun_yn(self):
        """ Return Sun Sensor -Y and init function"""
        return self._sun_yn, self._init_sun_minusy

    @hardware
    def sun_zn(self):
        """ Return Sun Sensor -Z and init function"""
        return self._sun_zn, self._init_sun_minusz

    @hardware
    def sun_xn(self):
        """ Return Sun Sensor -X and init function"""
        return self._sun_xn, self._init_sun_minusx

    @hardware
    def sun_yp(self):
        """ Return Sun Sensor +Y and init function"""
        return self._sun_yp, self._init_sun_plusy

    @hardware
    def sun_zp(self):
        """ Return Sun Sensor +Z and init function"""
        return self._sun_zp, self._init_sun_plusz

    @hardware
    def sun_xp(self):
        """ Return Sun Sensor +X and init function"""
        return self._sun_xp, self._init_sun_plusx

    @hardware
    def drv_x(self):
        """ Return Coil Driver X and init function"""
        return self._drv_x, self._init_coildriverx

    @hardware
    def drv_y(self):
        """ Return Coil Driver Y and init function"""
        return self._drv_y, self._init_coildrivery

    @hardware
    def drv_z(self):
        """ Return Coil Driver Z and init function"""
        return self._drv_z, self._init_coildriverz

    @hardware
    def burnwire1(self):
        """ Return Burnwire1 object and init function"""
        return self._burnwire1, self._init_burnwire1

    @hardware
    def burnwire2(self):
        """ Return Burnwire2 object and init function"""
        return self._burnwire2, self._init_burnwire2


# initialize Satellite as cubesat
_cubesat = _Satellite()

# Make radio and microcontroller accessible
radio = _cubesat.radio
cubesat_microcontroller = _cubesat.micro
BOOTTIME = _cubesat.BOOTTIME
