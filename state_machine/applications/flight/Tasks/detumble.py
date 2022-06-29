from numpy import identity, asarray, linalg, cross, matmul, atleast_2d, isnan, any

from lib.template_task import Task
import time

def bcross(b, ω, k=7e-4):
    b = (asarray(b))
    ω = (asarray(ω))
    b_hat = b / linalg.norm(b)
    bbt = matmul(atleast_2d(b_hat).T, atleast_2d(b_hat))
    M = - k * matmul(identity(3) - bbt, ω)
    # control
    m = 1 / (linalg.norm(b)) * (cross(b_hat, M))
    if any(isnan(m)):
        return [0, 0, 0]
    return m

def toStr(arr):
    return f'[{", ".join(map(str, arr))}]'

class task(Task):
    name = 'detubmle'
    color = 'pink'

    rgb_on = False

    async def main_task(self):
        b = (asarray(self.cubesat.magnetic))

        m = bcross(self.cubesat.magnetic, self.cubesat.gyro)

        self.debug(f'Detumbling with magnetorquer set to {m}')
        self.debug(f'M = m x b = {cross(m, b)}')

        # replace with calls to pycubed lib once it is ready
        print(f">>>m{m}")
        print(f">>>t{time.monotonic_ns()}")
