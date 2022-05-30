# Blink the RGB LED

from Tasks.template_task import Task

class task(Task):
    name='blink'
    color = 'pink'

    rgb_on = False
    async def main_task(self):
        if self.rgb_on:
            self.cubesat.RGB=(0,0,0)
            self.rgb_on=False
        else:
            self.cubesat.RGB=(0,255,0)
            self.rgb_on=True



