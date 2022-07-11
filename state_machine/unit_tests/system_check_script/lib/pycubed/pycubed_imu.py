"""
CircuitPython driver for PyCubed satellite IMU
PyCubed Mini mainboard-v02 for Pocketqube Mission
* Author(s): Max Holliday, Yashika Batra
"""
from pycubed import pocketqube as cubesat
from pycubed_logging import log


if cubesat.hardware['IMU']:
    def acceleration():
        """
        return the accelerometer reading from the IMU
        """
        return cubesat.IMU.accel

    def magnetic():
        """
        return the magnetometer reading from the IMU
        """
        return cubesat.IMU.mag

    def gyro():
        """
        return the gyroscope reading from the IMU
        """
        return cubesat.IMU.gyro

    def temperature():
        """
        return the thermometer reading from the IMU
        """
        return cubesat.IMU.temperature  # Celsius
else:
    log("IMU accessed without being initialized")
