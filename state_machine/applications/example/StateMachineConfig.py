from Tasks.battery_task import task as battery
from Tasks.time_task import task as time
from Tasks.every_5_seconds import task as every5
from Tasks.transition_task import task as transition

from TransitionFunctions import announcer

TaskMap = {
    'Battery': battery,
    'Transition': transition,
    'Time': time,
    'Every5Seconds': every5,
}

TransitionFunctionMap = {
    'Announcer': announcer
}

config = {
    'Normal': {
        'Tasks': {
            'Every5Seconds': {
                'Interval': 5,
                'Priority': 3,
                'ScheduleLater': False
            },
            'Battery': {
                'Interval': 10,
                'Priority': 5,
                'ScheduleLater': False
            },
            'Time': {
                'Interval': 7,
                'Priority': 4,
                'ScheduleLater': False
            },
            'Transition': {
                'Interval': 20,
                'Priority': 1,
                'ScheduleLater': True
            }
        },
        'StepsTo': ['Special'],
        'EnterFunctions': ['Announcer'],
        'ExitFunctions': ['Announcer'],
    },
    'Special': {
        'Tasks': {
            'Battery': {
                'Interval': 3.0,
                'Priority': 1,
                'ScheduleLater': False
            },
            'Transition': {
                'Interval': 15,
                'Priority': 1,
                'ScheduleLater': True
            },
        },
        'StepsTo': ['Normal']
    },
}
