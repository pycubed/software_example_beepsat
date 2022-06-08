from lib.template_task import Task


class task(Task):
    name = 'transition'
    color = 'blue'

    async def main_task(self):
        if self.cubesat.state_machine.state == 'Normal':
            self.debug(f'Switching to Special mode')
            self.cubesat.state_machine.switch_to('Special')
        else:
            self.debug(f'Switching to Normal mode')
            self.cubesat.state_machine.switch_to('Normal')
