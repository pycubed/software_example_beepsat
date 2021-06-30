# Import cubesat- Starting point of all programs

from pycubed import cubesat

import os
import sys

for f in os.listdir("Tasks"):
    if f == "stop_tasks.py" or f=="task.py":
        continue
    str = "Tasks." + f[:-3]
    obj = __import__(str, globals(), locals(), [], 0)
    if obj.Task(cubesat).schedule_later == False:
        cubesat.scheduled_objects.append(
            cubesat.schedule(
                obj.Task(cubesat).frequency,
                obj.Task(cubesat).main_task,
                obj.Task(cubesat).priority,
                obj.Task(cubesat).task_id,
            )
        )
    else:
        cubesat.scheduled_objects.append(
            cubesat.schedule_later(
                obj.Task(cubesat).frequency,
                obj.Task(cubesat).main_task,
                obj.Task(cubesat).priority,
                obj.Task(cubesat).task_id,
            )
        )

cubesat.run()
