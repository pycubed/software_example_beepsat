import tasko
# import lib.yaml as yaml

from TaskMap import TaskMap


def typecheck_props(state_name, task_name, props):
    # pylint: disable=unidiomatic-typecheck
    # using isinstance makes bools be considered ints.
    if type(props['Interval']) == int:
        props['Interval'] = float(props['Interval'])
    if type(props['Interval']) != float:
        raise ValueError(
            f'{state_name}->{task_name}->Interval should be int or float not {type(props["Interval"])}')

    if type(props['Priority']) == int:
        props['Priority'] = float(props['Interval'])
    if type(props['Priority']) != float:
        raise ValueError(
            f'{state_name}->{task_name}->Priority should be int or float not {type(props["Priority"])}')

    if type(props['ScheduleLater']) != bool:
        raise ValueError(
            f'{state_name}->{task_name}->ScheduleLater should be bool not {type(props["ScheduleLater"])}')


def validate_config(config):
    """Validates that the config file is well formed"""
    for state_name, state in config.items():
        for task_name, props in state['Tasks'].items():
            if task_name not in TaskMap:
                raise ValueError(
                    f'{task_name} defined in the {state_name} state, but {task_name} is not defined')
            if 'Interval' not in props:
                raise ValueError(f'Interval value not defined in {state_name}')
            if 'Priority' not in props:
                raise ValueError(f'Priority value not defined in {state_name}')
            if 'ScheduleLater' not in props:
                props['ScheduleLater'] = False  # default to false
            typecheck_props(state_name, task_name, props)
        if 'StepsTo' not in state:
            raise ValueError(
                f'The state {state_name} does not have StepsTo defined')
        if not isinstance(state['StepsTo'], list):
            raise ValueError(
                f'{state_name}->StepsTo should be bool list not {type(state["StepsTo"])}')
        for item in state['StepsTo']:
            if not isinstance(item, str):
                raise ValueError(
                    f'{state_name}->StepsTo should be bool list, but it contains an element of the wrong type')
            if not item in config:
                raise ValueError(
                    f'{state_name}->StepsTo defines a transition to {item} but {item} state is not defined'
                )


def load_state_machine():
    """Loads the state machine from the yaml file passed"""
    from StateMachineConfig import config
    validate_config(config)
    return config


class StateMachine:
    """Singleton State Machine Class"""

    def __init__(self, cubesat, start_state):
        self.config = load_state_machine()
        self.state = start_state

        # create shared asyncio object
        self.tasko = tasko

        # supports legacy code, only the state machine should use tasko
        cubesat.tasko = tasko

        # init task objects
        self.tasks = {key: task(cubesat) for key, task in TaskMap.items()}

        # set scheduled tasks to none
        self.scheduled_tasks = {}

        # Make state machine accesible to cubesat
        cubesat.state_machine = self

        # switch to start state, and start event loop
        self.switch_to(start_state, force=True)
        self.tasko.run()

    def stop_all(self):
        """Stops all running tasko processes"""
        for _, task in self.scheduled_tasks.items():
            task.stop()

    def switch_to(self, state_name, force=False):
        """Switches the state of the cubesat to the new state"""

        # prevent (or force) illegal transitions
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
