import time
import tasko

import lib.reader as reader
try:
    from ulab.numpy import array
except ImportError:
    from numpy import array

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
        return "something we recieved over radio"

    @property
    def last_rssi(self):
        return 147

    def sleep(self):
        self.listening = False

    def send(self, packet, destination=0x00, keep_listening=True):
        return None

    def send_with_ack(self, packet, keep_listening=True):
        return True


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
RGB = (0, 0, 0)
def setRGB(v):
    global RGB
    RGB = v

def getRGB():
    return RGB


vlowbatt = 4.0
BOOTTIME = time.monotonic()
data_cache = {}
def battery_voltage():
    return 6.4


def sim():
    return _cubesat.sim

def log(self, str):
    """Logs to sd card"""
    str = (str[:20] + '...') if len(str) > 23 else str
    print(f'log not implemented, tried to log: {str}')


"""
Sun Sensor Functions
"""

def sun_vector():
    """Returns the sun pointing vector in the body frame"""
    return array([0, 0, 0])


"""
Radio related functions
"""
# send = _cubesat.radio.send
# listen = _cubesat.radio.listen
await_rx = _cubesat.radio.await_rx
receive = _cubesat.radio.receive
sleep = _cubesat.radio.sleep
radio = _cubesat.radio
