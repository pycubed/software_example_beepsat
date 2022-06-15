import time

class Sattelite:
    tasko = None

    def __init__(self):
        self.battery_voltage = 6.4
        self.vlowbatt = 4.0
        self.BOOTTIME = time.monotonic()

    @property
    def acceleration(self):
        return (0.0, 0.0, 0.0)

    @property
    def magnetic(self):
        return (0.0, 0.0, 0.0)

    @property
    def gyro(self):
        return (0.0, 0.0, 0.0)


pocketqube = Sattelite()
