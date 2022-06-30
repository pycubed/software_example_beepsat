"""
Radio Task:

Manages all radio communication for the cubesat.
"""
from lib.template_task import Task
import lib.transmission_queue as tq

ANTENNA_ATTACHED = False

def should_transmit():
    """
    Return if we should transmit
    """
    return ANTENNA_ATTACHED

class task(Task):
    name = 'radio'
    color = 'teal'

    def __init__(self, satellite):
        # Copy pasted from beacon_task.py, not sure about the purpose
        # Or if we need it for our protocol.
        super().__init__(satellite)
        # set our radiohead node ID so we can get ACKs
        self.cubesat.radio.node = 0xFA  # our ID
        self.cubesat.radio.destination = 0xAB  # target's ID

    async def main_task(self):
        if tq.empty():
            self.debug("No packets to send")
            self.cubesat.radio.listen()
            heard_something = await self.cubesat.radio.await_rx(timeout=10)
            if heard_something:
                response = self.cubesat.radio.receive(keep_listening=True, with_ack=ANTENNA_ATTACHED)
                if response is not None:
                    self.debug(f'Recieved msg: {response}, RSSI: {self.cubesat.radio.last_rssi - 137}')
                    # Processing recieved messages goes here
                    #  - Execute commands
                    #  - Mark messages as received (and remove from tq)
            else:
                self.debug('No packets received')
        elif should_transmit():
            packet, send_once = tq.peek().packet()
            self.debug(f'Transmission Queue {tq.queue}')
            if send_once:
                tq.pop()
            short_packet = str(packet)[:20] + "...." if len(packet) > 23 else packet
            self.debug(f"Sending packet: {short_packet}")
            self.cubesat.radio.send(packet, destination=0xFF, keep_listening=True)
        self.cubesat.radio.sleep()
