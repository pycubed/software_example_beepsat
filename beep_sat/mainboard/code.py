# Beep-Sat Demo

import os
from supervisor import reload
from pycubed import cubesat


# schedule all tasks in directory
for file in os.listdir('Tasks'):
    # ignore these files
    if file in ("template_task.py","test_task.py","listen_task.py"):
        continue
    # auto-magically import the task files
    exec('import Tasks.{}'.format(file[:-3]))
    # create a helper object for scheduling the task
    task_obj=eval('Tasks.'+file[:-3]).task(cubesat)

    # determine if the task wishes to be scheduled later
    if hasattr(task_obj,'schedule_later'):
        schedule=cubesat.tasko.schedule_later
    else:
        schedule=cubesat.tasko.schedule

    # schedule each task object and add it to our dict
    cubesat.scheduled_tasks[task_obj.name]=schedule(task_obj.frequency,task_obj.main_task,task_obj.priority)

cubesat.tasko.run()

# try:
#     cubesat.tasko.run()
# except Exception as e:
#     try:
#         cubesat.log(',soft reset,{}'.format(e))
#         from supervisor import reload
#         reload()
#     except:
#         cubesat.micro.on_next_reset(cubesat.micro.RunMode.NORMAL)
#         cubesat.micro.reset()

# cubesat.micro.on_next_reset(cubesat.micro.RunMode.NORMAL)
# cubesat.micro.reset()
