# Transmit "Hello World" beacon

from lib.template_task import Task
import time
import os
import logs

class task(Task):
    name = 'beacon'
    color = 'teal'

    async def main_task(self):
        """
        Pushes a beacon packet onto the transmission queue.
        """
        currTime = time.time()
        TIMEINTERVAL = 1000

        try:
            beacon_packet = logs.beacon_packet(self)
            file = open(f"/sd/logs/log{int(currTime//TIMEINTERVAL)}.txt", "ab+")
            file.write(bytearray(beacon_packet))
            file.close()
        except Exception:
            try:
                os.mkdir('/sd/logs/')
            except Exception as e:
                self.debug(e)
