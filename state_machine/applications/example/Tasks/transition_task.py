from lib.template_task import Task
import lib.pycubed as cubesat


class task(Task):
    name = 'transition'
    color = 'blue'

    async def main_task(self):
        if cubesat.state_machine.state == 'Normal':
            self.debug('Switching to Special mode')
            cubesat.state_machine.switch_to('Special')
        else:
            self.debug('Switching to Normal mode')
            cubesat.state_machine.switch_to('Normal')
