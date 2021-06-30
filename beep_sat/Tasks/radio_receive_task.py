# Task to listen for "killswitch" command on Radio

import Tasks.stop_tasks as stop_tasks

class Task:
    def __init__(self, satellite):
        self.cubesat = satellite
        self.include = True
        self.cubesat.radio2.listen()

    def __await__(self):

        while self.cubesat.radio2.rx_done() == 0:
            yield
        message = self.cubesat.radio2.receive()
        msg_text = str(message, "ascii")
        if msg_text == "killswitch":
            print("Sending message.....")
            self.cubesat.radio2.send(
                "Killswitch received, Bye World......", keep_listening=True
            )

            #Stop desired tasks
            stop_tasks.StopTask(self.cubesat, 3, [1,2,3]).stop()

    async def main_task(self):
        print("Awaiting message")
        await self
        print("Done awaiting message")

    priority = 1
    frequency = 1
    task_id = 1
    schedule_later= False
