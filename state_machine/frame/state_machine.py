import tasko

from StateMachineConfig import config, TaskMap, TransitionFunctionMap
from lib.state_machine_utils import validate_config


class StateMachine:
    """Singleton State Machine Class"""

    def __init__(self, cubesat, start_state):
        self.config = config
        validate_config(config, TaskMap, TransitionFunctionMap)

        self.state = start_state

        # allow access to cubesat object
        self.cubesat = cubesat

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

        # execute transition functions
        if self.state != state_name:
            for fn in config[self.state]['ExitFunctions']:
                fn = TransitionFunctionMap[fn]
                fn(self.state, state_name, self.cubesat)
            for fn in config[state_name]['EnterFunctions']:
                fn = TransitionFunctionMap[fn]
                fn(self.state, state_name, self.cubesat)

        # reschedule tasks
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
            task_fn = self.tasks[task_name]._run

            self.scheduled_tasks[task_name] = schedule(
                frequency, task_fn, priority)
