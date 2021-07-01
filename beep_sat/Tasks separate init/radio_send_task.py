# Task to send "Hello World" on the radio

from Tasks.template_task import Task

class task(Task):
    priority = 3
    frequency = 1
    task_id = 3

    # def __init__(self, satellite):
    #     self.cubesat = satellite

    async def main_task(self):
        print("Sending message from PyCubed....")
        self.cubesat.radio1.send("Hello World!", keep_listening=True)
        print("Message sent from PyCubed")



