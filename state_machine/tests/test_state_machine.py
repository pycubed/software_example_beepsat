import unittest
import sys

sys.path.insert(0, '../frame')
sys.path.insert(0, '../applications/flight')

from state_machine import validate_config  # noqa: E402


tests = [
    {
        'TaskMap': {
            't1': True,
            't2': True,
            't3': True,
        }, 'TransitionFunctionMap': {
            'tf1': True,
            'tf2': True,
        },
        'config': {
            'Normal': {
                'Tasks': {
                    't1': {
                        'Interval': 10,
                        'Priority': 3,
                        'ScheduleLater': False
                    },
                    't2': {
                        'Interval': 10,
                        'Priority': 3,
                        'ScheduleLater': False
                    },
                    't3': {
                        'Interval': 10,
                        'Priority': 3,
                        'ScheduleLater': False
                    },
                },
                'StepsTo': ['LowPower', 'DeTumble'],
                'EnterFunctions': ['tf1'],
                'ExitFunctions': ['tf2'],
            },
            'LowPower': {
                'Tasks': {
                    't3': {
                        'Interval': 15.0,
                        'Priority': 1,
                        'ScheduleLater': False
                    },
                },
                'StepsTo': ['Normal']
            },
            'DeTumble': {
                'Tasks': {
                    't2': {
                        'Interval': 15.0,
                        'Priority': 3,
                        'ScheduleLater': False
                    },
                },
                'StepsTo': ['Normal']
            }
        },
        'Error': False
    }, {
        'TaskMap': {
            't1': True,
            't2': True,
            't3': True,
        }, 'TransitionFunctionMap': {
            'tf1': True,
            'tf2': True,
        },
        'config': {
            'Normal': {
                'Tasks': {
                    't1': {
                        'Interval': 10,
                        'Priority': 3,
                        'ScheduleLater': False
                    },
                    't2': {
                        'Interval': 10,
                        'Priority': 3,
                        'ScheduleLater': False
                    },
                    't3': {
                        'Interval': 10,
                        'Priorty': 3,
                        'ScheduleLater': False
                    },
                },
                'StepsTo': ['LowPower', 'DeTumble'],
                'EnterFunctions': ['tf1'],
                'ExitFunctions': ['tf2'],
            },
            'LowPower': {
                'Tasks': {
                    't3': {
                        'Interval': 15.0,
                        'Priority': 1,
                        'ScheduleLater': False
                    },
                },
                'StepsTo': ['Normal']
            },
            'DeTumble': {
                'Tasks': {
                    't2': {
                        'Interval': 15.0,
                        'Priority': 3,
                        'ScheduleLater': False
                    },
                },
                'StepsTo': ['Normal']
            }
        },
        'Error': True
    }
]


class TestValidateConfig(unittest.TestCase):

    def test(self):
        for v in tests:
            try:
                validate_config(v['config'], v['TaskMap'], v['TransitionFunctionMap'])
            except ValueError:
                self.assertTrue(v['Error'])
                continue
            self.assertTrue(not v['Error'])
