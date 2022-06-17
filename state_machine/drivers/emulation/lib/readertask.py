from lib.template_task import Task
import sys

class task(Task):
    name = 'reader'
    color = 'blue'

    rgb_on = False

    async def main_task(self):
        print('hi')
        data = sys.stdin.readline()
        print(data)
