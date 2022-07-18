from Tasks.battery_task import task as battery
from Tasks.beacon_task import task as beacon
from Tasks.blink_task import task as blink
from Tasks.imu_task import task as imu
from Tasks.time_task import task as time
from Tasks.detumble import task as detumble

from TransitionFunctions import announcer, low_power_on, low_power_off

from config import config  # noqa: F401

TaskMap = {
    'Battery': battery,
    'Beacon': beacon,
    'Blink': blink,
    'IMU': imu,
    'Time': time,
    'Detumble': detumble,
}

TransitionFunctionMap = {
    'Announcer': announcer,
    'LowPowerOn': low_power_on,
    'LowPowerOff': low_power_off,
}
