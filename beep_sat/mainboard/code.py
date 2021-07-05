# Beep-Sat Demo

import os
from pycubed import cubesat

print('-'*30+'\nBeep-Sat Demo\n'+'-'*30)

# schedule all tasks in directory
for file in os.listdir('Tasks'):
    # remove the '.py' from file name
    file=file[:-3]

    # ignore these files
    if file in ("template_task","test_task","listen_task"):
        continue

    # auto-magically import the task files
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

# runs forever
cubesat.tasko.run()
