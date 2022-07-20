from lib.template_task import Task
from lib.control import bcross
import time


def toStr(arr):
    return f'[{", ".join(map(str, arr))}]'

class task(Task):
    name = 'detumble'
    color = 'pink'

    rgb_on = False

    async def main_task(self):
        m = bcross(self.cubesat.magnetic, self.cubesat.gyro)

        # replace with calls to pycubed lib once it is ready
        if hasattr(self.cubesat, 'sim') and self.cubesat.sim:  # detects if we are hooked up to simulator
            print(f">>>m{toStr(m)}")
            print(f">>>t{time.monotonic_ns()}")
