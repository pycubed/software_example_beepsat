# Task to send "Hello World" on the radio

from Tasks.template_task import Task

class task(Task):
    priority = 1
    frequency = 1/30 # once every 30s
    name='beacon'
    color = 'teal'

    schedule_later=True

    async def main_task(self):
        # build beacon packet


        self.debug("Sending beacon")
        # only send if there's an antenna attached!
        self.cubesat.radio1.send("Hello World!",keep_listening=True)

        self.debug("Listening 10s for response (non-blocking)")
        heard_something = await self.cubesat.radio1.await_rx(timeout=10)

        if heard_something:
            response = self.cubesat.radio1.receive(keep_listening=True)
            if response is not None:
                self.debug("packet received!")
                print('\t  └──',response)
                self.cubesat.c_gs_resp+=1
        else:
            self.debug('no messages')
            self.cubesat.radio1.sleep()
        self.debug('finished')


