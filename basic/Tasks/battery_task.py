# check for low battery condition

from Tasks.template_task import Task

class task(Task):
    priority = 3
    frequency = 1/10 # once every 10s
    name='vbatt'
    color = 'orange'

    async def main_task(self):
        vbatt=self.cubesat.battery_voltage
        comp_var = ''

        if vbatt > self.cubesat.vlowbatt:
            comp_var = '>'
        else:
            comp_var = '<'

        self.debug(f'{vbatt:.1f}V {comp_var} threshold: {self.cubesat.vlowbatt:.1f}V')
