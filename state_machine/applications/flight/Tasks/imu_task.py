# Task to obtain IMU sensor readings

from lib.template_task import Task
import lib.pycubed as cubesat
import msgpack
from os import stat

SEND_DATA = False  # make sure you have an antenna attached!


class task(Task):
    name = 'imu'
    color = 'green'
    data_file = None

    # we want to initialize the data file only once upon boot
    # so perform our task init and use that as a chance to init the data files
    def __init__(self, satellite):
        super().__init__(satellite)

    async def main_task(self):
        # take IMU readings
        readings = {
            'accel': cubesat.acceleration(),
            'mag':   cubesat.magnetic(),
            'gyro':  cubesat.gyro(),
        }

        # store them in our cubesat data_cache object
        cubesat.data_cache.update({'imu': readings})

        # print the readings with some fancy formatting
        self.debug('IMU readings (x,y,z)')
        for imu_type in cubesat.data_cache['imu']:
            self.debug(f'{imu_type:>5} {cubesat.data_cache["imu"][imu_type]}', 2)
