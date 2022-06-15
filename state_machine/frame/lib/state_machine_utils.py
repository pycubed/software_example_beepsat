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


def validate_config(config, TaskMap, TransitionFunctionMap):
    """Validates that the config file is well formed"""
    for state_name, state in config.items():
        for task_name, props in state['Tasks'].items():
            if task_name not in TaskMap:
                raise ValueError(
                    f'{task_name} defined in the {state_name} state, but the task {task_name} is not defined')
            if 'Interval' not in props:
                raise ValueError(f'Interval value not defined in {state_name}->{task_name}')
            if 'Priority' not in props:
                raise ValueError(f'Priority value not defined in {state_name}->{task_name}')
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
            if item not in config:
                raise ValueError(
                    f'{state_name}->StepsTo defines a transition to {item} but {item} state is not defined'
                )
        if 'EnterFunctions' not in state:
            state['EnterFunctions'] = []
        prop = state['EnterFunctions']
        if not isinstance(prop, list):
            raise ValueError(f'{state_name}->EnterFunctions should be an array not {type(prop)}')

        if 'ExitFunctions' not in state:
            state['ExitFunctions'] = []
        prop = state['ExitFunctions']
        if not isinstance(prop, list):
            raise ValueError(f'{state_name}->EnterFunctions should be an array not {type(prop)}')
        valid_keys = {'Tasks', 'StepsTo', 'EnterFunctions', 'ExitFunctions'}
        for key in state.keys():
            if key not in valid_keys:
                raise ValueError(f'{state_name}->{key} should not be defined, choose one of {valid_keys}')
