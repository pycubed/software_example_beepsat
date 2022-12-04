import time
import tasko

from radio_driver import Radio
import reader as reader
import random
try:
    from ulab.numpy import array
except ImportError:
    from numpy import array

class Burnwire:
    def __init__(self):
        pass

    def duty_cycle(self, duty_cycle):
        assert 0 <= duty_cycle <= 0xffff


"""
Define HardwareInitException
"""
class HardwareInitException(Exception):
    pass


class Satellite:
    tasko = None
    _RGB = (0, 0, 0)
    vlowbatt = 4.0
    BOOTTIME = time.monotonic()
    data_cache = {}

    # Max opperating temp on specsheet for ATSAMD51J19A (Celsius)
    HIGH_TEMP = 125
    # Min opperating temp on specsheet for ATSAMD51J19A (Celsius)
    LOW_TEMP = -40
    # Low battery voltage threshold
    LOW_VOLTAGE = 4.0

    def __init__(self):
        self.task = None
        self.scheduled_tasks = {}

        self.radio = Radio()
        self.burnwire1 = Burnwire()

        self.data_cache = {}
        self.c_gs_resp = 1
        self.c_state_err = 0
        self.c_boot = None
        self.f_contact = True

        # magnetometer and accelerometer chosen to be arbitrary non zero, non parallel values
        # to provide more interesting output from the b-cross controller.
        self._accel = array([1.0, 2.0, 3.0])
        self._mag = array([4.0, 3.0, 1.0])
        self._gyro = array([0.0, 0.0, 0.0])
        self._torque = [0, 0, 0]
        self._cpu_temp = 30

        # debug utilities
        self.sim = False
        self.randomize_voltage = False

    @property
    def acceleration(self):
        """ return the accelerometer reading from the IMU """
        reader.read(self)
        return self._accel

    @property
    def magnetic(self):
        """ return the magnetometer reading from the IMU """
        reader.read(self)
        return self._mag

    @property
    def gyro(self):
        """ return the gyroscope reading from the IMU """
        reader.read(self)
        return self._gyro

    @property
    def temperature_imu(self):
        """ return the thermometer reading from the IMU """
        reader.read(self)
        return 20  # Celsius

    @property
    def temperature_cpu(self):
        """ return the temperature reading from the CPU in celsius """
        return 50  # Celsius

    @property
    def RGB(self):
        return self._RGB

    @RGB.setter
    def RGB(self, v):
        self._RGB = v

    @property
    def battery_voltage(self):
        reader.read(self)
        random_offset = - 0.5 + random.random() if self.randomize_voltage else 0
        return self.LOW_VOLTAGE + 0.01 + random_offset

    def log(self, str):
        """Logs to sd card"""
        str = (str[:20] + '...') if len(str) > 23 else str
        print(f'log not implemented, tried to log: {str}')

    @property
    def sun_vector(self):
        """Returns the sun pointing vector in the body frame"""
        return array([0, 0, 0])

    @property
    def imu(self):
        return True

    @property
    def neopixel(self):
        return True

    async def burn(self, dutycycle=0.5, duration=1):
        """
        Activates the burnwire for a given duration and dutycycle.
        """
        try:
            burnwire = self.burnwire1
            self.RGB = (255, 0, 0)

            # set the burnwire's dutycycle; begins the burn
            burnwire.duty_cycle = int(dutycycle * (0xFFFF))
            await tasko.sleep(duration)  # wait for given duration

            # set burnwire's dutycycle back to 0; ends the burn
            burnwire.duty_cycle = 0
            self.RGB = (0, 0, 0)

            self._deployA = True  # sets deployment variable to true
            return True
        except Exception as e:
            print('[ERROR][Burning]', e)
            return False


cubesat = Satellite()
