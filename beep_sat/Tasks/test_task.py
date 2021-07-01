from Tasks.template_task import Task

class task(Task):
    priority = 1
    frequency = 1
    task_id = 20

    # if the task needs to run code at the start
    def __init__(self,satellite):
        super(self.__class__, self).__init__(satellite)
        self.cubesat.radio1.listen()


    async def main_task(self):
        print('vbatt: {}'.format(self.cubesat.battery_voltage))


