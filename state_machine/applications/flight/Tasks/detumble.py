
from numpy import identity, asarray, linalg, cross, matmul, atleast_2d, ndarray

from lib.template_task import Task


def toStr(arr):
    return f'[{", ".join(map(str, arr))}]'

class task(Task):
    name = 'detubmle'
    color = 'pink'

    rgb_on = False

    async def main_task(self):
        b = (asarray(self.cubesat.magnetic))
        ω = (asarray(self.cubesat.gyro))
        k = 7e-4
        b_hat = b / linalg.norm(b)
        bbt = matmul(atleast_2d(b_hat).T, atleast_2d(b_hat))
        M = - k * matmul(identity(3) - bbt, ω)
        # control
        m = 1 / (linalg.norm(b)) * (cross(b_hat, M))
        self.cubesat._torque = ndarray.tolist(M)
        self.debug(f'Detumble with magnetorquer set to {toStr(m)}')
        # print(f'>>>m{toStr(m)}]')
        # print(f'>>>M[{toStr(M)}]')
        # print(f'{identity(3)}')
