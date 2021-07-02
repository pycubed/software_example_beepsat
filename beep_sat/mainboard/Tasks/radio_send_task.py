# Task to send "Hello World" on the radio

from Tasks.template_task import Task

class task(Task):
    priority = 1
    frequency = 1/30
    name='beacon'
    color = 'blue'

    async def main_task(self):
        # build beacon packet


        self.debug("Sending beacon")
        # only send if there's an antenna attached!
        self.cubesat.radio1.send("Hello World!",keep_listening=True)

        self.debug("Listening 10s for response (blocking)")
        response = self.cubesat.radio1.receive(timeout=10,keep_listening=True)
        if response is not None:
            print("Heard: {}".format(response))
            self.cubesat.c_gs_resp+=1



