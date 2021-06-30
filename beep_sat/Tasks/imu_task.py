# Task to obtain IMU sensor readings

class Task:
    def __init__(self, satellite):
        self.cubesat = satellite

    async def main_task(self):
        reading = self.cubesat.IMU.gyro
        print("Sending Gyro Readings....")
        self.cubesat.radio2.send(','.join(map(str,reading)), keep_listening=True)
        print("Done Sending Gyro Readings")

    priority = 2
    frequency = 1/10
    task_id = 2
    schedule_later=False
