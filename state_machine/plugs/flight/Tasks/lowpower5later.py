from lib.template_task import Task


class task(Task):
    name = 'test'
    color = 'gray'

    async def main_task(self):
        self.debug('low power 15 (later)')
        self.cubesat.state_machine.switch_to('Normal')
