from lib.template_task import Task
from pycubed import cubesat
from state_machine import state_machine


class deployment_manager(Task):
    name = 'depoloyment_manager'
    color = 'blue'

    rgb_on = False

    async def main_task(self):
        """
        Manages deployment by activating burnwires when appropriate,
        and switching to normal operations if contact is established.
        """
        if (cubesat.f_contact):
            self.debug('Contact with ground station has been already established, switching to Normal mode')
            state_machine.switch_to('Normal')
        else:
            if await cubesat.burn(duration=15):
                self.debug('Successfully burned')
            else:
                # Consider panic mode
                self.debug('Unsuccessful burn')
