from Tasks.template_task import Task

class task(Task):
    priority = 255
    frequency = 2 # twice per 1s
    name='blink'
    color = 'pink'

    rgb_on = False
    async def main_task(self):
        if self.rgb_on:
            self.cubesat.RGB=(0,0,0)
            self.rgb_on=False
        else:
            self.cubesat.RGB=(255,100,100)
            self.rgb_on=True



