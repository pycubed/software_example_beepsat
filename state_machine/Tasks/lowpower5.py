from Tasks.template_task import Task

class task(Task):
    name = 'test'
    color = 'gray'

    async def main_task(self):
        self.debug('low power 5')
