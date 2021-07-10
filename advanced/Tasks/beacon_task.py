# Transmit "Hello World" beacon

from Tasks.template_task import Task

ANTENNA_ATTACHED = False

class task(Task):
    priority = 1
    frequency = 1/30 # once every 30s
    name='beacon'
    color = 'teal'

    schedule_later = True

    async def main_task(self):
        """
        If you've attached a 433MHz antenna,
        set the above ANTENNA_ATTACHED variable to True
        to actually send the beacon packet
        """
        if ANTENNA_ATTACHED:
            self.debug("Sending beacon")
            self.cubesat.radio1.send("Hello World!",keep_listening=True)
        else:
            # Fake beacon since we don't know if an antenna is attached
            print() # blank line
            self.debug("[WARNING]")
            self.debug("NOT sending beacon (unknown antenna state)",2)
            self.debug("If you've attached an antenna, edit '/Tasks/beacon_task.py' to actually beacon", 2)
            print() # blank line
            self.cubesat.radio1.listen()

        self.debug("Listening 10s for response (non-blocking)")
        heard_something = await self.cubesat.radio1.await_rx(timeout=10)

        if heard_something:
            response = self.cubesat.radio1.receive(keep_listening=False)
            if response is not None:
                self.debug("packet received")
                self.debug('msg: {}, RSSI: {}'.format(response,self.cubesat.radio1.last_rssi-137),2)
                self.cubesat.c_gs_resp+=1
        else:
            self.debug('no messages')
        self.cubesat.radio1.sleep()
        self.debug('finished')


