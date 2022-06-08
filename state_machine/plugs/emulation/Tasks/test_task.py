from lib.template_task import Task
import time


class task(Task):
    name = 'test'
    color = 'gray'

    async def main_task(self):
        self.debug('test start: {}'.format(time.monotonic()))
        await self.cubesat.tasko.sleep(30)
        self.debug(f'test stop: {time.monotonic()}, switching to low power mode')
        self.cubesat.state_machine.switch_to('LowPower')
