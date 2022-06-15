import unittest
import sys

sys.path.insert(0, './state_machine/frame')

from lib.state_machine_utils import validate_config  # noqa: E402

basicTM = {
    't1': True,
    't2': True,
    't3': True,
}

basicTFM = {
    'tf1': True,
    'tf2': True,
}


tests = [
    {
        'TaskMap': basicTM,
        'TransitionFunctionMap': basicTFM,
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
                'StepsTo': ['Normal'],
            },
            'DeTumble': {
                'Tasks': {
                    't2': {
                        'Interval': 15.0,
                        'Priority': 3,
                        'ScheduleLater': False
                    },
                },
                'StepsTo': ['Normal'],
            }
        },
        'Valid': True,
        'Title': 'Large Correct Config',
    }, {
        'TaskMap': basicTM,
        'TransitionFunctionMap': basicTFM,
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
                'StepsTo': ['Normal'],
            }
        },
        'Valid': False,
        'Title': 'Large Incorrect Config (Normal->t3 Priority mispelled)',
    }, {
        'TaskMap': basicTM,
        'TransitionFunctionMap': basicTFM,
        'config': {
            'N': {
                'Tasks': {
                    't1': {
                        'Interval': 10,
                        'Priority': 3,
                        'ScheduleLater': False
                    },
                },
                'StepsTo': [],
            },
        },
        'Valid': True,
        'Title': 'Small Correct Config',
    }, {
        'TaskMap': basicTM,
        'TransitionFunctionMap': basicTFM,
        'config': {
            'N': {
                'Tasks': {
                    't5': {
                        'Interval': 10,
                        'Priority': 3,
                        'ScheduleLater': False
                    },
                },
                'StepsTo': [],
            },
        },
        'Valid': False,
        'Title': 'Wrong task name (t5 instead of t1/t2/t3)',
    }
]


class TestValidateConfig(unittest.TestCase):

    def test(self):
        for v in tests:
            try:
                validate_config(v['config'], v['TaskMap'], v['TransitionFunctionMap'])
            except ValueError as err:
                if v['Valid']:
                    print(err)
                    print(f'Incorrect result for test named {v["Title"]}')
                    self.assertTrue(False)
                continue
            if not v['Valid']:
                print(f'Incorrect result for test named {v["Title"]}')
            self.assertTrue(v['Valid'])
