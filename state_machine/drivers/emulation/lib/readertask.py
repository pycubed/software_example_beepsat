from lib.template_task import Task
import sys
import select
import json

from numpy import identity, asarray, linalg, matmul, atleast_2d, ndarray

class task(Task):
    name = 'reader'
    color = 'blue'

    rgb_on = False

    async def main_task(self):
        while select.select([sys.stdin, ], [], [], 0.0)[0]:
            data = sys.stdin.readline()
            if len(data) > 3 and data[0:3] == ">>>":
                # print(data)
                if data[3] == 'ω':
                    # print(data[4:])
                    self.cubesat._gyro = json.loads(data[4:])
                if data[3] == 'b':
                    # print(data[4:])
                    self.cubesat._mag = json.loads(data[4:])
                if data[3] == '?':
                    b = (asarray(self.cubesat.magnetic))
                    ω = (asarray(self.cubesat.gyro))
                    k = 7e-4
                    b_hat = b / linalg.norm(b)
                    bbt = matmul(atleast_2d(b_hat).T, atleast_2d(b_hat))
                    M = - k * matmul(identity(3) - bbt, ω)
                    self.cubesat._torque = ndarray.tolist(M)
                    print(f'>>>M{json.dumps(self.cubesat._torque)}')
