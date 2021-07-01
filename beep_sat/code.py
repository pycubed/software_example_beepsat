# Import cubesat- Starting point of all programs

from pycubed import cubesat
import os


# schedule all tasks in the directory
for file in os.listdir('Tasks'):
    # ignore these files
    if file in ("stop_tasks.py","template_task.py"):
        continue

    # auto-magically import the task files
    exec('import Tasks.{}'.format(file[:-3]))
    # create a helper object
    task_obj=eval('Tasks.'+file[:-3]).Task

    # schedule each task object and add it to our list
    cubesat.scheduled_tasks.append(
        cubesat.tasko.schedule(
            task_obj(cubesat).frequency,
            task_obj(cubesat).main_task,
            task_obj(cubesat).priority,
            task_obj(cubesat).task_id,
        )
    )

cubesat.tasko.run()
