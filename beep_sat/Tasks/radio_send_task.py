# Task to send "Hello World" on the radio

class Task:
    def __init__(self, satellite):
        self.cubesat = satellite

    async def main_task(self):
        print("Sending message from PyCubed....")
        self.cubesat.radio2.send("Hello World!", keep_listening=True)
        print("Message sent from PyCubed")

    priority = 3
    frequency = 1
    task_id = 3
    schedule_later=False

