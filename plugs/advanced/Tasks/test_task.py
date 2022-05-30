from Tasks.template_task import Task
import time

class task(Task):
    name = 'test'
    color = 'gray'

    schedule_later = True

    async def main_task(self):
        self.debug('test start: {}'.format(time.monotonic()))
        await self.cubesat.tasko.sleep(10)
        self.debug('test stop: {}'.format(time.monotonic()))
