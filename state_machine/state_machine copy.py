import tasko
import lib.yaml as yaml

from Tasks.battery_task import task as battery
from Tasks.beacon_task import task as beacon
from Tasks.blink_task import task as blink
from Tasks.imu_task import task as imu
from Tasks.time_task import task as time

TaskMap = {
    "Battery": battery,
    "Beacon": beacon,
    "Blink": blink,
    "IMU": imu,
    "Time": time,
}

start_state = 'Normal'


def load_state_machine():
    config_file = open("statemachine.yaml", "r")
    config = config_file.read()
    config_file.close()
    return yaml.safe_load(config)


def start_state_machine(cubesat):

    state_machine = load_state_machine()

    # create asyncio object
    cubesat.tasko = tasko

    # init task objects
    Tasks = {key: task(cubesat) for key, task in TaskMap.items()}

    # set current state
    state = state_machine[start_state]

    for task_name, props in state['Tasks'].items():
        if props['ScheduleLater']:
            schedule = cubesat.tasko.schedule_later
        else:
            schedule = cubesat.tasko.schedule

        frequency = 1 / props['Interval']
        priority = props['Priority']
        task_fn = Tasks[task_name]
        print(task_fn)
        cubesat.scheduled_tasks[task_name] = schedule(
            frequency, task_fn, priority)
