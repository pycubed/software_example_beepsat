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
            'Burn Wire 2': False,
            'WDT': False  # Watch Dog Timer pending
        }
        self.micro = microcontroller
        self.data_cache = {}
        self.filenumbers = {}
        self.vlowbatt = 3.5
        self.debug = True
        self._vbatt = analogio.AnalogIn(board.BATTERY)  # Define battery voltage

        # Define and initialize hardware
        self.__init_i2c__()
        self.__init_spi__()
        self.__init_sdcard__()
        self.__init_neopixel__()
        self.__init_imu__()
        self.__init_radio__()
        self.__init_sun_sensors__()
        self.__init_coil_drivers__()
        self.__init_burnwires__()

    def __init_i2c__(self):
        """ Define I2C buses and initialize one at a time """
        try:
            self.i2c1 = busio.I2C(board.SCL1, board.SDA1)
            self.hardware['I2C1'] = True
        except Exception as e:
            print("[ERROR][Initializing I2C1]", e)

        try:
            self.i2c2 = busio.I2C(board.SCL2, board.SDA2)
            self.hardware['I2C2'] = True
        except Exception as e:
            print("[ERROR][Initializing I2C2]", e)

        try:
            self.i2c3 = busio.I2C(board.SCL3, board.SDA3)
            self.hardware['I2C3'] = True
        except Exception as e:
            print("[ERROR][Initializing I2C3]", e)

    def __init_spi__(self):
        """ Define and initialize SPI bus """
        try:
            self.spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
            self.hardware['SPI'] = True
        except Exception as e:
            print("[ERROR][Initializing SPI]", e)

    def __init_sdcard__(self):
        """ Define SD Parameters and initialize SD Card """
        try:
            self._sd = sdcardio.SDCard(self.spi, board.CS_SD, baudrate=4000000)
            self._vfs = storage.VfsFat(self._sd)
            storage.mount(self._vfs, "/sd")
            sys.path.append("/sd")
            self.hardware['SDcard'] = True
        except Exception as e:
            print('[ERROR][Initializing SD Card]', e)

    def __init_neopixel__(self):
        """ Define neopixel parameters and initialize """
        try:
            self.neopixel = neopixel.NeoPixel(
                board.NEOPIXEL, 1, brightness=0.2, pixel_order=neopixel.GRB)
            self.neopixel[0] = (0, 0, 0)
            self.hardware['Neopixel'] = True
        except Exception as e:
            print('[WARNING][Neopixel]', e)

    def __init_imu__(self):
        """ Define IMU parameters and initialize """
        try:
            self.IMU = bmx160.BMX160_I2C(self.i2c1, address=0x68)
            self.hardware['IMU'] = True
        except Exception as e:
            print(f'[ERROR][Initializing IMU] {e}\n\tMaybe try address=0x68?')

    def __init_radio__(self):
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
            self.radio = pycubed_rfm9x.RFM9x(
                self.spi, self._rf_cs, self._rf_rst,
                self.UHF_FREQ, rfm95pw=True)
            self.radio.dio0 = self.radio_DIO0
            self.radio.sleep()
            self.hardware['Radio'] = True
        except Exception as e:
            print('[ERROR][Initializing RADIO]', e)

    def __init_sun_sensors__(self):
        """ Initialize sun sensors one at a time """
        sun_sensors = []

        try:
            sun_yn = adafruit_tsl2561.TSL2561(self.i2c2, address=0x29)  # -Y
            sun_sensors.append(sun_yn)
            self.hardware['Sun -Y'] = True
        except Exception as e:
            print('[ERROR][Initializing Sun Sensor -Y]', e)

        try:
            sun_zn = adafruit_tsl2561.TSL2561(self.i2c2, address=0x39)  # -Z
            sun_sensors.append(sun_zn)
            self.hardware['Sun -Z'] = True
        except Exception as e:
            print('[ERROR][Initializing Sun Sensor -Z]', e)

        try:
            sun_xn = adafruit_tsl2561.TSL2561(self.i2c1, address=0x49)  # -X
            sun_sensors.append(sun_xn)
            self.hardware['Sun -X'] = True
        except Exception as e:
            print('[ERROR][Initializing Sun Sensor -X]', e)

        try:
            sun_yp = adafruit_tsl2561.TSL2561(self.i2c1, address=0x29)  # +Y
            sun_sensors.append(sun_yp)
            self.hardware['Sun +Y'] = True
        except Exception as e:
            print('[ERROR][Initializing Sun Sensor +Y]', e)

        try:
            sun_zp = adafruit_tsl2561.TSL2561(self.i2c1, address=0x39)  # +Z
            sun_sensors.append(sun_zp)
            self.hardware['Sun +Z'] = True
        except Exception as e:
            print('[ERROR][Initializing Sun Sensor +Z]', e)

        try:
            sun_xp = adafruit_tsl2561.TSL2561(self.i2c2, address=0x49)  # +X
            sun_sensors.append(sun_xp)
            self.hardware['Sun +X'] = True
        except Exception as e:
            print('[ERROR][Initializing Sun Sensor +X]', e)

        for i in sun_sensors:
            i.enabled = False  # set enabled status to False

        self.sun_sensors = sun_sensors

    def __init_coil_drivers__(self):
        """ Initialize coil drivers one at a time """
        coil_drivers = []

        try:
            # may need to fix i2c addresses
            # schematic says U7 -> 0xC4 and 0xC5 but these vals are 8 bit instead of 7
            drv_x = drv8830.DRV8830(self.i2c1, 0x68)  # U7
            coil_drivers.append(drv_x)
            self.hardware['Coil X'] = True
        except Exception as e:
            print('[ERROR][Initializing H-Bridge U6]', e)

        try:
            # may need to fix i2c addresses
            # schematic says U8 -> 0xD0 and 0xD1 but these vals are 8 bit instead of 7
            drv_y = drv8830.DRV8830(self.i2c1, 0x60)  # U8
            coil_drivers.append(drv_y)
            self.hardware['Coil Y'] = True
        except Exception as e:
            print('[ERROR][Initializing H-Bridge U8]', e)

        try:
            # may need to fix i2c addresses
            # schematic says U9 -> 0xC0 and 0xC1 but these vals are 8 bit instead of 7
            drv_z = drv8830.DRV8830(self.i2c1, 0x62)  # U9
            coil_drivers.append(drv_z)
            self.hardware['Coil Z'] = True
        except Exception as e:
            print('[ERROR][Initializing H-Bridge U4]', e)

        for driver in coil_drivers:
            driver.mode = drv8830.COAST
            driver.vout = 0

        self.coil_drivers = coil_drivers

    def __init_burnwires__(self):
        """ Define burnwire parameters and initialize """
        # TODO: update firmware so we can use board.BURN1 and board.BURN2
        # instead of microcontroller.pin.PA19 and microcontroller.pin.PA18

        burnwires = []

        try:
            # changed pinout from BURN1 to PA19 (BURN1 did not support PWMOut)
            self.burnwire1 = pwmio.PWMOut(
                microcontroller.pin.PA19, frequency=1000, duty_cycle=0)
            burnwires.append(self.burnwire1)
            self.hardware['Burn Wire 1'] = True
        except Exception as e:
            print('[ERROR][Initializing Burn Wire IC1]', e)

        try:
            # changed pinout from BURN2 to PA18 (BURN2 did not support PWMOut)
            self.burnwire2 = pwmio.PWMOut(
                microcontroller.pin.PA18, frequency=1000, duty_cycle=0)
            burnwires.append(self.burnwire2)
            # Initializing Burn Wire 2 hardware as false; no corresponding integrated circuit yet
            self.hardware['Burn Wire 2'] = False
        except Exception as e:
            print('[ERROR][Initializing Burn Wire IC2]', e)

        self.burnwires = burnwires

    def reinit(self, dev):
        """ Reinit: reinitialize radio, sd, or IMU based upon contents of dev """
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


# initialize Satellite as cubesat
cubesat = Satellite()

"""
IMU-related functions
TODO: cubesat.imu hardware check
"""

def acceleration():
    """ return the accelerometer reading from the IMU """
    return cubesat.IMU.accel

def magnetic():
    """ return the magnetometer reading from the IMU """
    return cubesat.IMU.mag

def gyro():
    """ return the gyroscope reading from the IMU """
    return cubesat.IMU.gyro

def temperature():
    """ return the thermometer reading from the IMU """
    return cubesat.IMU.temperature  # Celsius


"""
Burnwire-related functions
TODO: cubesat.burnwire1 hardware check
"""

def burn(burn_num='1', dutycycle=0, freq=1000, duration=1):
    """
    control the burnwire(s)
    initialize with burn_num = '1' ; burnwire 2 IC is not set up
    """
    # BURN1 = -Z,BURN2 = extra burnwire pin, dutycycle ~0.13%
    dtycycl = int((dutycycle / 100) * (0xFFFF))

    # print configuration information
    print('----- BURN WIRE CONFIGURATION -----')
    print(f'\tFrequency of: {freq}Hz')
    print(f'\tDuty cycle of: {100 * dtycycl / 0xFFFF}% (int:{dtycycl})')
    print(f'\tDuration of {duration}sec')

    # initialize burnwire based on the burn_num passed to the function
    if '1' in burn_num:
        burnwire = cubesat.burnwire1
    elif '2' in burn_num:
        return False  # return False because burnwire 2 IC is not set up
        # burnwire = self.burnwire2
    else:
        return False

    set_RGB(255, 0, 0)  # set RGB to red

    # set the burnwire's dutycycle; begins the burn
    burnwire.duty_cycle = dtycycl
    time.sleep(duration)  # wait for given duration

    # set burnwire's dutycycle back to 0; ends the burn
    burnwire.duty_cycle = 0
    set_RGB(0, 0, 0)  # set RGB to no color

    cubesat._deployA = True  # sets deployment variable to true
    burnwire.deinit()  # deinitialize burnwire

    return cubesat._deployA  # return true


"""
Radio related functions
TODO: cubesat.radio hardware check
Keeping the aliasing so we can do a hardware check for cubesat.radio
"""

def send(data, *, keep_listening=False, destination=None, node=None,
         identifier=None, flags=None):
    """ Wrap cubesat.radio.send to allow for hardware checks """
    cubesat.radio.send(data, keep_listening=keep_listening,
                       destination=destination, node=node, identifier=identifier,
                       flags=flags)

def listen():
    """ Wrap cubesat.radio.listen to allow for hardware checks """
    cubesat.radio.listen()

async def await_rx(timeout=60):
    """ Wrap cubesat.radio.await_rx to allow for hardware checks """
    cubesat.radio.await_rx(timeout=timeout)

def receive(*, keep_listening=True, with_header=False, with_ack=False,
            timeout=None, debug=False):
    """ Wrap cubesat.radio.receive to allow for hardware checks """
    cubesat.radio.receive(keep_listening=keep_listening, with_header=with_header,
                          with_ack=with_ack, timeout=timeout, debug=debug)

def sleep():
    """ Wrap cubesat.radio.sleep to allow for hardware checks """
    cubesat.radio.sleep()


"""
Miscellaneous statistic functions
TODO: cubesat.neopixel hardware check
"""

def temperature_cpu():
    """ return the temperature reading from the CPU """
    return cubesat.micro.cpu.temperature  # Celsius


def RGB():
    """ return the current RGB settings of the neopixel object """
    return cubesat.neopixel[0]


def set_RGB(value):
    """ set an RGB value to the neopixel object """
    if cubesat.hardware['Neopixel']:
        try:
            cubesat.neopixel[0] = value
        except Exception as e:
            print('[WARNING]', e)


def battery_voltage():
    """ return the battery voltage """
    # initialize vbat
    vbat = 0

    for _ in range(50):
        # 65536 = 2^16, number of increments we can have to voltage
        vbat += cubesat._vbatt.value * 3.3 / 65536

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
    cubesat.c_boot = 0


def incr_logfail_count():
    """ increment logfail count in non-volatile memory (nvm) """
    cubesat.c_logfail += 1


def reset_logfail_count():
    """ reset logfail count in non-volatile memory (nvm) """
    cubesat.c_logfail = 0
