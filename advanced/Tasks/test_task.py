from Tasks.template_task import Task
import time

class task(Task):
    priority = 4
    frequency = 1/30 # once every 30s
    name = 'test'
    color = 'gray'

    schedule_later = True

    async def main_task(self):
        self.debug(f'test start: {time.monotonic()}')
        await self.cubesat.tasko.sleep(10)
        self.debug(f'test stop: {time.monotonic()}')
