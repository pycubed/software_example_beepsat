# check for low battery condition

from lib.template_task import Task


class task(Task):
    name = 'vbatt'
    color = 'orange'

    timeout = 60 * 60  # 60 min

    async def main_task(self):
        vbatt = self.cubesat.battery_voltage
        if self.cubesat.state_machine.state == 'LowPower':
            if vbatt >= self.cubesat.vlowbatt:
                self.debug(f'{vbatt:.1f}V ≥ {self.cubesat.vlowbatt:.1f}V')
                self.debug('sufficient battery detected, switching out of low power mode', 2)
                self.cubesat.state_machine.switch_to('Normal')
            else:
                self.debug(f'{vbatt:.1f}V < {self.cubesat.vlowbatt:.1f}V')
        else:
            if vbatt < self.cubesat.vlowbatt:
                self.debug(f'{vbatt:.1f}V < {self.cubesat.vlowbatt:.1f}V')
                self.debug('low battery detected!', 2)
                # switch to low power state
                self.cubesat.state_machine.switch_to('LowPower')
            else:
                self.debug(f'{vbatt:.1f}V ≥ {self.cubesat.vlowbatt:.1f}V')
