from lib.template_task import Task
from pycubed import cubesat
from state_machine import state_machine
import time


INITIAL_BURN_DELAY = 5 * 60
BURN_INTERVAL = 24 * 60 * 60

class deployment_manager(Task):
    name = 'depoloyment_manager'
    color = 'blue'

    rgb_on = False
    start_time = time.time()
    last_burn = float('inf')

    async def main_task(self):
        if (cubesat.f_contact):
            self.debug('Contact with ground station has been already established, switching to Normal mode')
            state_machine.switch_to('Normal')
        elif self.should_burn():
            self.last_burn = time.time()
            if await cubesat.burn(duration=10, duty_cycle=0.2):
                cubesat.f_burn = True
                self.debug('Successfully burned')
            else:
                self.debug('Unsuccessful burn')

    def should_burn(self):
        if (time.time() - self.start_time) > INITIAL_BURN_DELAY:  # first burn
            return True
        elif (time.time() - self.last_burn) > BURN_INTERVAL:  # other burns
            return True
        return False
