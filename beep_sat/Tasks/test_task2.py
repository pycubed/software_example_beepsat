from Tasks.template_task import Task

class task(Task):
    priority = 2
    frequency = 1
    task_id = 19


    async def main_task(self):
        print('vbatt2: {}'.format(self.cubesat.battery_voltage))


