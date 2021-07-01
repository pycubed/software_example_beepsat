from Tasks.template_task import Task

class task(Task):
    priority = 1
    frequency = 1
    task_id = 20

    async def main_task(self):
        print('vbatt: {}'.format(self.cubesat.battery_voltage))


