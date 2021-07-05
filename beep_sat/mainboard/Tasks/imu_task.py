# Task to obtain IMU sensor readings

from Tasks.template_task import Task

class task(Task):
    priority = 4
    frequency = 1/10 # once every 10s
    name='imu'
    color = 'green'

    async def main_task(self):
        # take IMU readings
        readings = {
            'accel':self.cubesat.acceleration,
            'mag':  self.cubesat.magnetic,
            'gyro': self.cubesat.gyro,
        }

        # store them in our cubesat data_cache object
        self.cubesat.data_cache.update({'imu':readings})

        # print the readings with some fancy formatting
        self.debug('IMU readings (x,y,z)')
        for imu_type in self.cubesat.data_cache['imu']:
            print('{}{:>5} {}'.format('\t  └── ',imu_type,self.cubesat.data_cache['imu'][imu_type]))



