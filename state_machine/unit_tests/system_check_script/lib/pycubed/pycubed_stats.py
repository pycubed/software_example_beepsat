"""
CircuitPython driver for PyCubed satellite stats and sensors
PyCubed Mini mainboard-v02 for Pocketqube Mission
* Author(s): Max Holliday, Yashika Batra
"""
from pycubed import pocketqube as cubesat
import time

def temperature_cpu():
    """
    return the temperature reading from the CPU
    """
    return cubesat.micro.cpu.temperature  # Celsius


def RGB():
    """
    return the current RBG settings of the neopixel object
    """
    return cubesat.neopixel[0]


def set_RGB(value):
    """
    set an RGB value to the neopixel object
    """
    if cubesat.hardware['Neopixel']:
        try:
            cubesat.neopixel[0] = value
        except Exception as e:
            print('[WARNING]', e)


def battery_voltage():
    """
    return the battery voltage
    """
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
    """
    report battery voltage as % full
    """
    return 100 * cubesat.battery_voltage / 4.2


def timeon():
    """
    return the time on a monotonic clock
    """
    return int(time.monotonic())


def reset_boot_count():
    """
    reset boot count in non-volatile memory (nvm)
    """
    cubesat.c_boot.__set__(0)


def incr_logfail_count():
    """
    increment logfail count in non-volatile memory (nvm)
    """
    current_count = cubesat.c_logfail.__get__()
    cubesat.c_logfail.__set__(current_count + 1)


def reset_logfail_count():
    """
    reset logfail count in non-volatile memory (nvm)
    """
    cubesat.c_logfail.__set__(0)
