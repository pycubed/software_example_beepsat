# Import cubesat- Starting point of all programs

from pycubed import cubesat
import os


for file in os.listdir('Tasks'):
    if file == "stop_tasks.py" or file=="task.py":
        continue
    exec('import Tasks.{}'.format(file[:-3]))

    task=eval('Tasks.'+file[:-3])

    cubesat.scheduled_objects.append(
        cubesat.tasko.schedule(
            task.Task(cubesat).frequency,
            task.Task(cubesat).main_task,
            task.Task(cubesat).priority,
            task.Task(cubesat).task_id,
        )
    )

cubesat.tasko.run()
