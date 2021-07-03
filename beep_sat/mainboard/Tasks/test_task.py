from Tasks.template_task import Task

class task(Task):
    priority = 4
    frequency = 1/10 # once every 10s
    name='test'
    color = 'gray'

    async def main_task(self):
        self.debug('test task')


