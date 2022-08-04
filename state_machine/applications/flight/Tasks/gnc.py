from lib.template_task import Task
from lib.control import bcross
import lib.pycubed as cubesat
from lib.IGRF import igrf_eci
from lib.sun_position import approx_sun_position_ECI
import lib.orbital_mechanics as orbital_mechanics
import lib.mekf as mekf
import time
try:
    from ulab.numpy import array
except ImportError:
    from numpy import array


def toStr(arr):
    return f'[{", ".join(map(str, arr))}]'

class task(Task):
    name = 'detumble'
    color = 'pink'

    rgb_on = False
    last = None
    r_eci = array([6871, -6571, -7071])

    async def main_task(self):

        # compute control
        m = bcross(cubesat.magnetic(), cubesat.gyro())

        # replace with calls to pycubed lib once it is ready
        if hasattr(cubesat, 'sim') and cubesat.sim():  # detects if we are hooked up to simulator
            print(f">>>m{toStr(m)}")
            print(f">>>t{time.monotonic_ns()}")

        self.last = time.monotonic()
