import tasko
import lib.yaml as yaml

from Tasks.battery_task import task as battery
from Tasks.beacon_task import task as beacon
from Tasks.blink_task import task as blink
from Tasks.imu_task import task as imu
from Tasks.time_task import task as time
from Tasks.test_task import task as test
from Tasks.lowpower5 import task as lowpower5
from Tasks.lowpower5later import task as lowpower5later

TaskMap = {
    "Battery": battery,
    "Beacon": beacon,
    "Blink": blink,
    "IMU": imu,
    "Time": time,
    "Test": test,
    "LowPower5": lowpower5,
    "LowPower5Later": lowpower5later,
}


def load_state_machine(file):
    """Loads the state machine from the yaml file passed"""
    config_file = open(file, "r")
    config = config_file.read()
    config_file.close()
    config = yaml.safe_load(config)
    # check that everything is defined
    for state_name, state in config.items():
        for task_name, props in state['Tasks'].items():
            if not task_name in TaskMap:
                raise ValueError(
                    f'{task_name} defined in the {state_name} state, but {task_name} is not defined')
            if not 'Interval' in props:
                raise ValueError(f'Interval value not defined in {state_name}')
            if not 'Priority' in props:
                raise ValueError(f'Priority value not defined in {state_name}')
            if not 'ScheduleLater' in props:
                props['ScheduleLater'] = False  # default to false

    return config


class StateMachine:
    """Singleton State Machine Class"""

    def __init__(self, cubesat, start_state, config_file_path):
        self.config = load_state_machine(config_file_path)
        self.state = start_state

        # create shared asyncio object
        self.tasko = tasko
        # left to support legacy code, only the state machine should interact with tasko if possible
        cubesat.tasko = tasko

        # init task objects
        self.tasks = {key: task(cubesat) for key, task in TaskMap.items()}

        # set scheduled tasks to none
        self.scheduled_tasks = {}

        # Make state machine accesible to cubesat
        cubesat.state_machine = self

        # switch to start state
        self.switch_to(start_state, force=True)
        self.tasko.run()

    def stop_all(self):
        """Kills all running tasko processes"""
        for _, task in self.scheduled_tasks.items():
            task.stop()

    def switch_to(self, state_name, force=False):
        """Switches the state of the cubesat to the new state"""

        if not(state_name in self.config[self.state]['StepsTo'] or force):
            raise ValueError(
                f'You cannot transition from {self.state} to {state_name}')

        self.stop_all()
        self.scheduled_tasks = {}
        self.state = state_name
        state_config = self.config[state_name]

        for task_name, props in state_config['Tasks'].items():
            if props['ScheduleLater']:
                schedule = self.tasko.schedule_later
            else:
                schedule = self.tasko.schedule

            frequency = 1 / props['Interval']
            priority = props['Priority']
            task_fn = self.tasks[task_name].main_task

            self.scheduled_tasks[task_name] = schedule(
                frequency, task_fn, priority)
