# Transmit "Hello World" beacon

from Tasks.template_task import Task
from cdh import message_handler

ANTENNA_ATTACHED = True

class task(Task):
    priority = 1
    frequency = 1/30 # once every 30s
    name='beacon'
    color = 'teal'

    schedule_later = True

    def __init__(self,satellite):
        super().__init__(satellite)
        # set our radiohead node ID so we can get ACKs
        self.cubesat.radio1.node = self.cubesat.cfg['id'] # our ID
        self.cubesat.radio1.destination = self.cubesat.cfg['gs'] # target's ID

    async def main_task(self):
        """
        If you've attached a 433MHz antenna,
        set the above ANTENNA_ATTACHED variable to True
        to actually send the beacon packet

        TODO: dynamic radio config
              beacon at one config, RX on another
        """
        if ANTENNA_ATTACHED:
            self.debug("Sending beacon")
            self.cubesat.radio1.send("Hello World!",destination=0xFF,keep_listening=True)
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
            # retrieve response but don't ACK back unless an antenna is attached
            response = self.cubesat.radio1.receive(keep_listening=True,with_ack=ANTENNA_ATTACHED,with_header=True,view=True)
            if response is not None:
                self.debug("packet received")
                self.debug('msg: {}, RSSI: {}'.format(bytes(response),self.cubesat.radio1.last_rssi-137),2)
                self.cubesat.c_gs_resp+=1

                """
                ########### ADVANCED ###########
                Over-the-air commands
                See beep-sat guide for more details
                """
                if not ANTENNA_ATTACHED:
                    self.debug('Antenna not attached. Skipping over-the-air command handling')
                else:
                    # parsing and command dispatch handled in /lib/cdh.py
                    message_handler(self.cubesat,response)
        else:
            self.debug('no messages')
        self.cubesat.radio1.sleep()
        self.debug('finished')
