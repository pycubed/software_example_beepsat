from Tasks.battery_task import task as battery
from Tasks.beacon_task import task as beacon
from Tasks.blink_task import task as blink
from Tasks.imu_task import task as imu
from Tasks.time_task import task as time
from Tasks.detumble import task as detumble
from Tasks.radio import task as radio
from TransitionFunctions import announcer, low_power_on, low_power_off
from config import config  # noqa: F401

TaskMap = {
    'Battery': battery,
    'Beacon': beacon,
    'Blink': blink,
    'IMU': imu,
    'Time': time,
    'Detumble': detumble,
    'Radio': radio,
}

TransitionFunctionMap = {
    'Announcer': announcer,
    'LowPowerOn': low_power_on,
    'LowPowerOff': low_power_off,
}

config = {
    'Normal': {
        'Tasks': {
            'Battery': {
                'Interval': 10,
                'Priority': 3,
                'ScheduleLater': False
            },
            'IMU': {
                'Interval': 10,
                'Priority': 5,
                'ScheduleLater': False
            },
            'Beacon': {
                'Interval': 30,
                'Priority': 1,
                'ScheduleLater': True
            },
            'Blink': {
                'Interval': 2,
                'Priority': 255,
                'ScheduleLater': False
            },
            'Time': {
                'Interval': 20,
                'Priority': 4,
                'ScheduleLater': False
            },
            'Detumble': {
                'Interval': 0.1,
                'Priority': 3,
                'ScheduleLater': False
            },
            'Radio': {
                'Interval': 5.0,
                'Priority': 3,
                'ScheduleLater': True
            }
        },
        'StepsTo': ['LowPower', 'DeTumble']
    },
    'LowPower': {
        'Tasks': {
            'Battery': {
                'Interval': 15.0,
                'Priority': 1,
                'ScheduleLater': False
            },
        },
        'StepsTo': ['Normal'],
        'EnterFunctions': ['Announcer', 'LowPowerOn'],
        'ExitFunctions': ['Announcer', 'LowPowerOff'],
    },
    'DeTumble': {
        'Tasks': {
            'Battery': {
                'Interval': 15.0,
                'Priority': 3,
                'ScheduleLater': False
            }
        },
        'StepsTo': ['Normal']
    }
}
