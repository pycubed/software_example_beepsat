# Blink the RGB LED

from lib.template_task import Task
from lib.pycubed import cubesat


class task(Task):
    name = 'blink'
    color = 'pink'

    rgb_on = False

    async def main_task(self):
        if self.rgb_on:
            cubesat.setRGB((0, 0, 0))
            self.rgb_on = False
        else:
            cubesat.setRGB((50, 0, 50))
            self.rgb_on = True
