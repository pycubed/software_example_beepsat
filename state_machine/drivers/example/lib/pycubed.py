import time

def acceleration():
    return (0.0, 0.0, 0.0)

def magnetic():
    return (0.0, 0.0, 0.0)

def gyro():
    return (0.0, 0.0, 0.0)

def temperature_imu():
    return 20

def battery_voltage():
    return 6.4


BOOTTIME = time.monotonic()
vlowbatt = 4.0
