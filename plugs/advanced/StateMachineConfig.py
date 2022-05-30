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
            'Test': {
                'Interval': 3,
                'Priority': 1,
                'ScheduleLater': False
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
            'LowPower5': {
                'Interval': 5.0,
                'Priority': 2,
                'ScheduleLater': False
            },
            'LowPower5Later': {
                'Interval': 15.0,
                'Priority': 2,
                'ScheduleLater': True
            }
        },
        'StepsTo': ['Normal']
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
