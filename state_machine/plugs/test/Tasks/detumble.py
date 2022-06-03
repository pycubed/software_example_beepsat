
from numpy import identity, asarray, linalg, cross, matmul, atleast_2d

from Tasks.template_task import Task


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
        print(f'detumbling with magnetorquer set to {m}')
        print(f'{M} = M = m x b = {cross(m,b)}')
        # print(f'{identity(3)}')
