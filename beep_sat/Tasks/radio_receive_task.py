# Task to listen for "killswitch" command on Radio

from Tasks.template_task import Task

class task(Task):
    priority = 1
    frequency = 1
    name='receive'

    # if the task needs to run code at the start
    def __init__(self,satellite):
        super(self.__class__, self).__init__(satellite)
        self.cubesat.radio1.listen()
        print('listening...')

    # this should be moved to radio library for generic await receive
    def __await__(self):
        while not self.cubesat.radio1.rx_done():
            yield
        message = self.cubesat.radio1.receive()
        print(message==b'killswitch')
        msg_text = str(message, "ascii")
        if msg_text == "killswitch":
            print("Sending message.....")
            self.cubesat.radio1.send(
                "Killswitch received, Bye World......", keep_listening=True
            )

            #Stop all tasks
            for t in self.cubesat.scheduled_tasks:
                print('Stopping {} task'.format(t))
                self.cubesat.scheduled_tasks[t].stop()

    async def main_task(self):
        print("Awaiting message")
        self.cubesat.radio1.listen()
        await self
        print("Done awaiting message")


