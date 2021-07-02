# check for low battery condition

from Tasks.template_task import Task

class task(Task):
    priority = 3
    frequency = 1/10
    name='vbatt'
    color = 'white'

    async def main_task(self):
        vbatt=self.cubesat.battery_voltage
        self.debug('{:.1f}V, threshold: {:.1f}V'.format(vbatt,self.cubesat.vlowbatt))
        if vbatt < self.cubesat.vlowbatt:
            self.debug('low battery detected!')


