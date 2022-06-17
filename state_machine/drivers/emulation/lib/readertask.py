from lib.template_task import Task
import sys
import select
import json

class task(Task):
    name = 'reader'
    color = 'blue'

    rgb_on = False

    async def main_task(self):
        while select.select([sys.stdin, ], [], [], 0.0)[0]:
            data = sys.stdin.readline()
            if data[0:3] == ">>>":
                if data[3] == 'ω':
                    print(data[4:])
                    self.cubesat._gyro = json.loads(data[4:])
                if data[3] == 'b':
                    print(data[4:])
                    self.cubesat._mag = json.loads(data[4:])
