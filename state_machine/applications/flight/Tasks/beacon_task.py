# Transmit "Hello World" beacon

from lib.template_task import Task
import lib.transmission_queue as tq
from lib.message import Message

class task(Task):
    name = 'beacon'
    color = 'teal'

    async def main_task(self):
        """
        If you've attached a 433MHz antenna,
        set the above ANTENNA_ATTACHED variable to True
        to actually send the beacon packet
        """
        tq.push(Message(10, "Hello World!"))
