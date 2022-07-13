try:
    from ulab.numpy import eye as identity, array, linalg, cross, dot as matmul, isfinite, all
except Exception:
    from numpy import identity, array, linalg, cross, matmul, isfinite, all

from lib.template_task import Task
import time

def bcross(b, ω, k=7e-4):
    b = (array(b))
    ω = (array(ω))
    b_hat = b / linalg.norm(b)
    bbt = matmul(array([b_hat]).transpose(), array([b_hat]))
    M = - k * matmul(identity(3) - bbt, ω)
    # control
    m = 1 / (linalg.norm(b)) * (cross(b_hat, M))
    if all(isfinite(m)):
        return m
    return [0, 0, 0]

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
