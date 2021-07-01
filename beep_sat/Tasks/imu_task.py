# Task to obtain IMU sensor readings

from Tasks.template_task import Task

class task(Task):
    priority = 2
    frequency = 1/10
    name='imu'

    async def main_task(self):
        reading = self.cubesat.IMU.gyro
        print("Sending Gyro Readings....",reading)
        self.cubesat.radio1.send(','.join(map(str,reading)), keep_listening=True)
        print("Done Sending Gyro Readings")


