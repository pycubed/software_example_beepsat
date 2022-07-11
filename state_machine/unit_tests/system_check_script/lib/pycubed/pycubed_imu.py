"""
CircuitPython driver for PyCubed satellite IMU
PyCubed Mini mainboard-v02 for Pocketqube Mission
* Author(s): Max Holliday, Yashika Batra
"""
from pycubed import pocketqube as cubesat
from pycubed_logging import log


def check_imu():
    if cubesat.hardware['IMU']:
        return True
    else:
        log("IMU accessed without being initialized")
        return False

def acceleration():
    """
    return the accelerometer reading from the IMU
    """
    if check_imu():
        return cubesat.IMU.accel

def magnetic():
    """
    return the magnetometer reading from the IMU
    """
    if check_imu():
        return cubesat.IMU.mag

def gyro():
    """
    return the gyroscope reading from the IMU
    """
    if check_imu():
        return cubesat.IMU.gyro

def temperature():
    """
    return the thermometer reading from the IMU
    """
    if check_imu():
        return cubesat.IMU.temperature  # Celsius
