# check for low battery condition

from lib.template_task import Task


class task(Task):
    name = 'vbatt'
    color = 'orange'

    timeout = 60 * 60  # 60 min

    async def main_task(self):
        vbatt = self.cubesat.battery_voltage
        comp_var = ''

        if vbatt > self.cubesat.vlowbatt:
            comp_var = '>'
        else:
            comp_var = '<'

        self.debug(f'{vbatt:.1f}V {comp_var} threshold: {self.cubesat.vlowbatt:.1f}V')
