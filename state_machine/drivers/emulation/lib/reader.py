import sys
import select
import json

def read(cubesat):
    while select.select([sys.stdin, ], [], [], 0.0)[0]:
        data = sys.stdin.readline()
        if len(data) > 3 and data[0:3] == ">>>":
            # print(data)
            if data[3] == 'ω':
                cubesat._gyro = json.loads(data[4:])
            if data[3] == 'b':
                cubesat._mag = json.loads(data[4:])
