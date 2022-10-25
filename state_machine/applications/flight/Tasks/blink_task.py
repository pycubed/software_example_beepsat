# Blink the RGB LED

from lib.template_task import Task
from pycubed import cubesat


class task(Task):
    name = 'blink'
    color = 'pink'

    rgb_on = False

    async def main_task(self):
        if not cubesat.neopixel:
            self.debug('No neopixel attached, skipping blink task')
            return
        if self.rgb_on:
            cubesat.RGB = (0, 0, 0)
            self.rgb_on = False
        else:
            cubesat.RGB = (50, 0, 50)
            self.rgb_on = True
