# Task to obtain IMU sensor readings

from Tasks.template_task import Task

class task(Task):
    priority = 2
    frequency = 0.1
    task_id = 2

    # def __init__(self, satellite):
    #     self.cubesat = satellite

    async def main_task(self):
        reading = self.cubesat.IMU.gyro
        print("Sending Gyro Readings....",reading)
        self.cubesat.radio1.send(','.join(map(str,reading)), keep_listening=True)
        print("Done Sending Gyro Readings")


