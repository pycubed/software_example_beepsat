import time
import tasko

import lib.reader as reader

class Radio:
    def __init__(self):
        self.node = 0
        self.listening = False

    def listen(self):
        self.listening = True

    async def await_rx(self, timeout=60.0):
        """Wait timeout seconds to until you recieve a message, return true if message received false otherwise"""
        if not self.listening:
            return False
        _ = await tasko.sleep(timeout * 0.5)
        return True

    def receive(self, *, keep_listening=True, with_header=False, with_ack=False, timeout=None, debug=False):
        return "Hello World!"

    @property
    def last_rssi(self):
        return 147

    def sleep(self):
        self.listening = False


class Satellite:
    tasko = None

    def __init__(self):
        self.task = None
        self.scheduled_tasks = {}
        self.radio = Radio()
        self.data_cache = {}
        self.c_gs_resp = 1
        self.c_state_err = 0
        self.c_boot = None

        # magnetometer and accelerometer chosen to be arbitrary non zero, non parallel values
        # to provide more interesting output from the b-cross controller.
        self._accel = [1.0, 2.0, 3.0]
        self._mag = [4.0, 3.0, 1.0]
        self._gyro = [0.0, 0.0, 0.0]
        self._torque = [0, 0, 0]
        self.sim = False


_cubesat = Satellite()

"""
IMU-related functions
"""

def acceleration():
    """ return the accelerometer reading from the IMU """
    reader.read(_cubesat)
    return _cubesat._accel

def magnetic():
    """ return the magnetometer reading from the IMU """
    reader.read(_cubesat)
    return _cubesat._mag

def gyro():
    """ return the gyroscope reading from the IMU """
    reader.read(_cubesat)
    return _cubesat._gyro

def temperature_imu():
    """ return the thermometer reading from the IMU """
    reader.read(_cubesat)
    return 20  # Celsius


"""
Misc Functions
"""

vlowbatt = 4.0
BOOTTIME = time.monotonic()
data_cache = {}
def battery_voltage():
    return 6.4

def sim():
    return _cubesat.sim


"""
Radio related functions
"""
# send = _cubesat.radio.send
# listen = _cubesat.radio.listen
await_rx = _cubesat.radio.await_rx
receive = _cubesat.radio.receive
sleep = _cubesat.radio.sleep
radio = _cubesat.radio
