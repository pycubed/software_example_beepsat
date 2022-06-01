import time
import tasko


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
        _ = await tasko.sleep(timeout*0.5)
        return True

    def receive(self, *, keep_listening=True, with_header=False, with_ack=False, timeout=None, debug=False):
        return "Hello World!"

    @property
    def last_rssi(self):
        return 147

    def sleep(self):
        self.listening = False


class Sattelite:
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

    def new_file(self, substring, binary=False):
        print(
            f"new file not implemented, {substring} not written with binary={binary}")
        return None

    @property
    def acceleration(self):
        return (0.0, 0.0, 0.0)

    @property
    def magnetic(self):
        return (0.0, 0.0, 0.0)

    @property
    def gyro(self):
        return (0.0, 0.0, 0.0)

    def log(self, str):
        """Logs to sd card"""
        print(f'log not implemented')


pocketqube = Sattelite()
