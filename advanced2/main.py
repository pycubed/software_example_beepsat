"""
PyCubed Beep-Sat Demo (Advanced-2)
    - improved fault handling & tolerance
    - low power mode + deep sleep
    - logging data to sd card
    - over the air commands
    - deep sleep wake from radio

TODO: evaluate tasko vs adafruit_asyncio
M. Holliday
"""

print('\n{lines}\n{:^40}\n{:^40}\n{lines}\n'.format('Beep-Sat Demo','[ADVANCED-2]',lines='-'*40))

print('Initializing PyCubed Hardware...')
import os, tasko
from pycubed import cubesat

# create asyncio object
cubesat.tasko=tasko
# dict to store scheduled objects by name
cubesat.scheduled_tasks={}

if cubesat.radio1.hot_start:
    # battery must be above threshold or the low-batt timeout flag should be set
    if (cubesat.battery_voltage > cubesat.cfg['lb']) or cubesat.f_lowbtout:
        # try:
        print(f'hot start detected! -- radio1 msg: {cubesat.radio1.hot_start}')
        from cdh import hotstart_handler
        # radio params not set yet, but hotstart_handler() should use cubesat.cfg anyways so shouldn't be an issue
        hotstart_handler(cubesat, cubesat.radio1.hot_start)

print('Loading Tasks...',end='')
# schedule all tasks in directory
for file in os.listdir('Tasks'):
    # remove the '.py' from file name
    file=file[:-3]

    # ignore these files
    if file in ("template_task","test_task","listen_task"):
        continue

    # auto-magically import the task file
    exec('import Tasks.{}'.format(file))
    # create a helper object for scheduling the task
    task_obj=eval('Tasks.'+file).task(cubesat)

    # determine if the task wishes to be scheduled later
    if hasattr(task_obj,'schedule_later'):
        schedule=cubesat.tasko.schedule_later
    else:
        schedule=cubesat.tasko.schedule

    # schedule each task object and add it to our dict
    cubesat.scheduled_tasks[task_obj.name]=schedule(task_obj.frequency,task_obj.main_task,task_obj.priority)
print(len(cubesat.scheduled_tasks),'total')

print('Running...')
try:
    # should run forever
    cubesat.tasko.run()
except Exception as e:
    print('FATAL ERROR: {}'.format(e))
    try:
        # increment our NVM error counter
        cubesat.c_state_err+=1
        # try to log everything
        cubesat.log('{},{},{}'.format(e,cubesat.c_state_err,cubesat.c_boot))
    except:
        pass

# we shouldn't be here!
print('Engaging fail safe: hard reset')
from time import sleep
sleep(10)
cubesat.micro.on_next_reset(cubesat.micro.RunMode.NORMAL)
cubesat.micro.reset()
