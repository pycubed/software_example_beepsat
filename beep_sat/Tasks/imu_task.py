# Task to obtain IMU sensor readings

from Tasks.template_task import Task

class task(Task):
    priority = 4
    frequency = 1/10
    name='imu'
    color = 'green'

    async def main_task(self):
        reading = self.cubesat.IMU.gyro
        self.debug(reading)
        self.cubesat.data_cache['imu']=reading


