# Blink the RGB LED

from lib.template_task import Task
import lib.pycubed as cubesat


class task(Task):
    name = 'blink'
    color = 'pink'

    rgb_on = False

    async def main_task(self):
        if self.rgb_on:
            cubesat.set_RGB((0, 0, 0))
            self.rgb_on = False
        else:
            cubesat.set_RGB((0, 255, 0))
            self.rgb_on = True
