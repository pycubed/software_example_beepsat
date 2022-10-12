from lib.template_task import Task
from pycubed import cubesat
from state_machine import state_machine


class deployment_manager(Task):
    name = 'depoloyment_manager'
    color = 'blue'

    rgb_on = False

    async def main_task(self):
        # nvm shit
        if (cubesat.f_deploy):
            state_machine.switch_to('Normal')
        else:
            if await cubesat.burn(duration=15):
                self.deubg('Successfully burned')
            else:
                # Consider panic mode
                self.deubg('Uncuccessful burn')
