# Beep-Sat Demo

from pycubed import cubesat
import os

cnt=0
# schedule all tasks in the directory
for file in os.listdir('Tasks'):
    # ignore these files
    if file in ("template_task.py"):
        continue
    cnt+=1
    # auto-magically import the task files
    exec('import Tasks.{}'.format(file[:-3]))
    # create a helper object
    task_obj=eval('Tasks.'+file[:-3]).task(cubesat)

    # schedule each task object and add it to our dict
    cubesat.scheduled_tasks[task_obj.name]=cubesat.tasko.schedule(
        task_obj.frequency,task_obj.main_task,task_obj.priority)

print(cubesat.scheduled_tasks)

cubesat.tasko.run()
