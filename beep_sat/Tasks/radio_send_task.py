# Task to send "Hello World" on the radio

from Tasks.template_task import Task

class task(Task):
    priority = 3
    frequency = 1/20
    name='beacon'

    async def main_task(self):
        print("Sending message from PyCubed....")
        self.cubesat.radio1.send("Hello World!", keep_listening=True)
        print("Message sent from PyCubed")



