# Transmit "Hello World" beacon

from lib.template_task import Task
import radio_utils.transmission_queue as tq
from radio_utils.message import Message
import logs

class task(Task):
    name = 'beacon'
    color = 'teal'

    async def main_task(self):
        """
        Pushes a beacon packet onto the transmission queue.
        """

        beacon_packet = logs.beacon_packet()
        tq.push(Message(10, beacon_packet))
        self.debug("Beacon task pushing to tq")
