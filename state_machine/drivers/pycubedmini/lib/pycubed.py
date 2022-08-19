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

class device:
    """
    Based on the code from: https://docs.python.org/3/howto/descriptor.html#properties
    Attempts to return the appropriate hardware device.
    If this fails, it will attempt to reinitialize the hardware.
    If this fails again, it will raise an exception.
    """

    def __init__(self, fget=None):
        self.fget = fget
        self._device = None

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        if self.fget is None:
            raise AttributeError(f'unreadable attribute {self._name}')

        if self._device is not None:
            return self._device
        else:
            self._device = self.fget(instance)
            return self._device


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
    data_cache = {}

    # Satellite attributes
    LOW_VOLTAGE = 3.0
    # Max opperating temp on specsheet for ATSAMD51J19A (Celsius)
    HIGH_TEMP = 125
    # Min opperating temp on specsheet for ATSAMD51J19A (Celsius)
    LOW_TEMP = -40

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
        self.BOOTTIME = int(time.monotonic())  # get monotonic time at initialization
        self.micro = microcontroller
        self._vbatt = analogio.AnalogIn(board.BATTERY)  # Battery voltage

        # To force initialization of hardware
        self.i2c1
        self.i2c2
        self.i2c3
        self.spi
        self.sdcard
        self.neopixel
        self.imu
        self.radio
        self.sun_minusy
        self.sun_minusz
        self.sun_minusx
        self.sun_plusy
        self.sun_plusz
        self.sun_plusx
        self.coildriverx
        self.coildrivery
        self.coildriverz
        self.burnwire1
        self.burnwire2

    @device
    def i2c1(self):
        """ Initialize I2C1 bus """
        try:
            return busio.I2C(board.SCL1, board.SDA1)
        except Exception as e:
            print("[ERROR][Initializing I2C1]", e)

    @device
    def i2c2(self):
        """ Initialize I2C2 bus """
        try:
            return busio.I2C(board.SCL2, board.SDA2)
        except Exception as e:
            print("[ERROR][Initializing I2C2]", e)

    @device
    def i2c3(self):
        """ Initialize I2C3 bus """
        try:
            return busio.I2C(board.SCL3, board.SDA3)
        except Exception as e:
            print("[ERROR][Initializing I2C3]", e)

    @device
    def spi(self):
        """ Initialize SPI bus """
        try:
            return busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        except Exception as e:
            print("[ERROR][Initializing SPI]", e)

    @device
    def sdcard(self):
        """ Define SD Parameters and initialize SD Card """
        try:
            return sdcardio.SDCard(self.spi, board.CS_SD, baudrate=4000000)
        except Exception as e:
            print('[ERROR][Initializing SD Card]', e)

    @device
    def vfs(self):
        try:
            vfs = storage.VfsFat(self.sd)
            storage.mount(vfs, "/sd")
            sys.path.append("/sd")
            return vfs
        except Exception as e:
            print('[ERROR][Initializing VFS]', e)

    @device
    def neopixel(self):
        """ Define neopixel parameters and initialize """
        try:
            led = neopixel.NeoPixel(
                board.NEOPIXEL, 1, brightness=0.2, pixel_order=neopixel.GRB)
            led[0] = (0, 0, 0)
            return led
        except Exception as e:
            print('[ERROR][Initializing Neopixel]', e)

    @device
    def imu(self):
        """ Define IMU parameters and initialize """
        try:
            return bmx160.BMX160_I2C(self.i2c1, address=0x68)
        except Exception as e:
            print(f'[ERROR][Initializing IMU] {e}\n\tMaybe try address=0x68?')

    @device
    def radio(self):
        """ Define radio parameters and initialize UHF radio """
        try:
            self._rf_cs = digitalio.DigitalInOut(board.RF_CS)
            self._rf_rst = digitalio.DigitalInOut(board.RF_RST)
            self.radio_DIO0 = digitalio.DigitalInOut(board.RF_IO0)
            self.radio_DIO0.switch_to_input()
            self.radio_DIO1 = digitalio.DigitalInOut(board.RF_IO1)
            self.radio_DIO1.switch_to_input()
            self._rf_cs.switch_to_output(value=True)
            self._rf_rst.switch_to_output(value=True)
        except Exception as e:
            print('[ERROR][Initializing Radio]', e)

        try:
            radio = pycubed_rfm9x.RFM9x(
                self.spi, self._rf_cs, self._rf_rst,
                self.UHF_FREQ)
            radio.dio0 = self.radio_DIO0
            radio.node = 0xAB  # our ID
            radio.destination = 0xBA  # target's ID
            radio.sleep()
            return radio
        except Exception as e:
            print('[ERROR][Initializing RADIO]', e)

    @device
    def sun_yn(self):
        """ Initialize the -Y sun sensor on I2C2 """
        try:
            sun_yn = adafruit_tsl2561.TSL2561(self.i2c3, address=0x29)
            sun_yn.enabled = False
            return sun_yn
        except Exception as e:
            print('[ERROR][Initializing Sun Sensor -Y]', e)

    @device
    def sun_zn(self):
        """ Initialize the -Z sun sensor on I2C2 """
        try:
            sun_zn = adafruit_tsl2561.TSL2561(self.i2c3, address=0x39)
            sun_zn.enabled = False
            return sun_zn
        except Exception as e:
            print('[ERROR][Initializing Sun Sensor -Z]', e)

    @device
    def sun_xn(self):
        """ Initialize the -X sun sensor on I2C1 """
        try:
            sun_xn = adafruit_tsl2561.TSL2561(self.i2c2, address=0x29)
            sun_xn.enabled = False
            return sun_xn
        except Exception as e:
            print('[ERROR][Initializing Sun Sensor -X]', e)

    @device
    def sun_yp(self):
        """ Initialize the +Y sun sensor on I2C1 """
        try:
            sun_yp = adafruit_tsl2561.TSL2561(self.i2c3, address=0x49)
            sun_yp.enabled = False
            return sun_yp
        except Exception as e:
            print('[ERROR][Initializing Sun Sensor +Y]', e)

    @device
    def sun_zp(self):
        """ Initialize the +Z sun sensor on I2C1 """
        try:
            sun_zp = adafruit_tsl2561.TSL2561(self.i2c2, address=0x39)
            sun_zp.enabled = False
            return sun_zp
        except Exception as e:
            print('[ERROR][Initializing Sun Sensor +Z]', e)

    @device
    def sun_xp(self):
        """ Initialize the +X sun sensor on I2C2 """
        try:
            sun_xp = adafruit_tsl2561.TSL2561(self.i2c2, address=0x49)
            sun_xp.enabled = False
            return sun_xp
        except Exception as e:
            print('[ERROR][Initializing Sun Sensor +X]', e)

    @device
    def drv_x(self):
        """ Initialize Coil Driver X on I2C3, set mode and voltage """
        try:
            return drv8830.DRV8830(self.i2c1, 0xC4 >> 1)  # U7
        except Exception as e:
            print('[ERROR][Initializing H-Bridge U7]', e)

    @device
    def drv_y(self):
        """ Initialize Coil Driver Y on I2C3, set mode and voltage """
        try:
            return drv8830.DRV8830(self.i2c1, 0xC0 >> 1)  # U8
        except Exception as e:
            print('[ERROR][Initializing H-Bridge U8]', e)

    @device
    def drv_z(self):
        """ Initialize Coil Driver Z on I2C3, set mode and voltage """
        try:
            return drv8830.DRV8830(self.i2c1, 0xD0 >> 1)  # U9
        except Exception as e:
            print('[ERROR][Initializing H-Bridge U9]', e)

    @device
    def burnwire1(self):
        """ Initialize Burnwire1 on PA19 """
        # TODO: update firmware so we can use board.BURN1
        try:
            # changed pinout from BURN1 to PA19 (BURN1 did not support PWMOut)
            return pwmio.PWMOut(
                microcontroller.pin.PA19, frequency=1000, duty_cycle=0)
        except Exception as e:
            print('[ERROR][Initializing Burn Wire IC1]', e)

    @device
    def burnwire2(self):
        """ Initialize Burnwire2 on PA18 """
        # TODO: update firmware so we can use board.BURN2
        try:
            # changed pinout from BURN2 to PA18 (BURN2 did not support PWMOut)
            # Initializing Burn Wire 2 hardware as false; no corresponding IC
            return pwmio.PWMOut(
                microcontroller.pin.PA18, frequency=1000, duty_cycle=0)
        except Exception as e:
            print('[ERROR][Initializing Burn Wire IC2]', e)

    @property
    def acceleration(self):
        """ return the accelerometer reading from the IMU in m/s^2 """
        return self.imu.accel if self.imu else None

    @property
    def magnetic(self):
        """ return the magnetometer reading from the IMU in µT """
        return self.imu.mag if self.imu else None

    @property
    def gyro(self):
        """ return the gyroscope reading from the IMU in deg/s """
        return self.imu.gyro if self.imu else None

    @property
    def temperature_imu(self):
        """ return the thermometer reading from the IMU in celsius """
        return self.imu.temperature if self.imu else None

    @property
    def temperature_cpu(self):
        """ return the temperature reading from the CPU in celsius """
        return self.micro.cpu.temperature if self.micro else None

    def coildriver_vout(self, driver_index, projected_voltage):
        """ Set a given voltage for a given coil driver """
        if driver_index == "X" or driver_index == "U7":
            self.drv_x.throttle_volts = projected_voltage
        elif driver_index == "Y" or driver_index == "U8":
            self.drv_y.throttle_volts = projected_voltage
        elif driver_index == "Z" or driver_index == "U9":
            self.drv_z.throttle_volts = projected_voltage
        else:
            print(driver_index, "is not a defined coil driver")

    @property
    def battery_voltage(self):
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
            vbat += self._vbatt.value * 3.3 / 65536

        # vbat / 50 = average of all battery voltage values read
        # 100k/100k voltage divider
        voltage = (vbat / 50) * (100 + 100) / 100

        # volts
        return voltage

    @property
    def sun_vector(self):
        """Returns the sun pointing vector in the body frame"""
        return array(
            [self.sun_xp.lux - self.sun_xn.lux,
             self.sun_yp.lux - self.sun_yn.lux,
             self.sun_zp.lux - self.sun_zn.lux])

    def burn(self, burn_num='1', dutycycle=0, duration=1):
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
            burnwire = self.burnwire1
        elif '2' in burn_num:
            # because burnwire2 is not set up, will throw HardwareInitException
            burnwire = self.burnwire2
        else:
            print("Burnwire2 IC is not set up.")
            return False

        self.setRGB(255, 0, 0)  # set RGB to red

        # set the burnwire's dutycycle; begins the burn
        burnwire.duty_cycle = dtycycl
        time.sleep(duration)  # wait for given duration

        # set burnwire's dutycycle back to 0; ends the burn
        burnwire.duty_cycle = 0
        self.setRGB(0, 0, 0)  # set RGB to no color

        self._deployA = True  # sets deployment variable to true
        burnwire.deinit()  # deinitialize burnwire

        return self._deployA  # return true

    @property
    def RGB(self):
        return self.neopixel[0]

    @RGB.setter
    def RGB(self, v):
        self.neopixel[0] = v

    def timeon(self):
        """ return the time on a monotonic clock """
        return int(time.monotonic()) - self.BOOTTIME

    def reset_boot_count(self):
        """ reset boot count in non-volatile memory (nvm) """
        self.c_boot = 0

    def incr_logfail_count(self):
        """ increment logfail count in non-volatile memory (nvm) """
        self.c_logfail += 1

    def reset_logfail_count(self):
        """ reset logfail count in non-volatile memory (nvm) """
        self.c_logfail = 0


# initialize Satellite as cubesat
cubesat = _Satellite()
