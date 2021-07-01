from Tasks.template_task import Task

class task(Task):
    priority = 5
    frequency = 0.1
    name='test'

    async def main_task(self):
        print('vbatt: {}'.format(self.cubesat.battery_voltage))


