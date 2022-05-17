```
if hasattr(task_obj, 'schedule_later'):
    schedule = cubesat.tasko.schedule_later
else:
    schedule = cubesat.tasko.schedule
```
This is terrible (in main.py), if schedule_later is set to false it will still have the same behavior