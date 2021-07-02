from Tasks.template_task import Task

class task(Task):
    priority = 4
    frequency = 1/10
    name='test'
    color = 'gray'

    async def main_task(self):
        pass


