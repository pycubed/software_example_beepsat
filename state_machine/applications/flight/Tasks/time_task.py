# print the time in seconds since boot every 20 seconds

from lib.template_task import Task
import lib.pycubed as cubesat
import time


class task(Task):
    name = 'time'
    color = 'white'

    async def main_task(self):
        t_since_boot = time.monotonic() - cubesat.BOOTTIME
        self.debug('{:.3f}s since boot'.format(t_since_boot))
