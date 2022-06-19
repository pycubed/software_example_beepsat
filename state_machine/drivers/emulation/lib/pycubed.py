import time
import tasko

from lib.readertask import task as reader_task


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
        self.battery_voltage = 6.4
        self.vlowbatt = 4.0
        self.BOOTTIME = time.monotonic()
        self.radio = Radio()
        self.data_cache = {}
        self.c_gs_resp = 1
        self.c_state_err = 0
        self.c_boot = None

        schedule = tasko.schedule
        rt = reader_task(self)
        self.reader_task = schedule(100, rt.main_task, 10)  # try to read from stdin at 100Hz

        self._accel = (1.0, 2.0, 3.0)
        self._mag = (4.0, 3.0, 1.0)
        self._gyro = (0.0, 0.0, 0.0)
        self._torque = [0, 0, 0]

    def new_file(self, substring, binary=False):
        print(
            f"new file not implemented, string not written with binary={binary}")
        return None

    @property
    def acceleration(self):
        return self._accel

    @property
    def magnetic(self):
        return self._mag

    @property
    def gyro(self):
        return self._gyro

    def log(self, str):
        """Logs to sd card"""
        print('log not implemented')


pocketqube = Satellite()
