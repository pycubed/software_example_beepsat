# Transmit "Hello World" beacon

from lib.template_task import Task
import radio_utils.transmission_queue as tq
from radio_utils.message import Message
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
        logDir = os.path.join(os.getcwd(), ".sd")

        try:
            file = open(f".sd/logfiles/log{int(currTime//TIMEINTERVAL)}.txt", "ab+")
        except FileNotFoundError:
            try:
                os.mkdir(logDir)
                os.mkdir(os.path.join(logDir, "logfiles"))
                file = open(f".sd/logfiles/log{int(currTime//TIMEINTERVAL)}.txt", "ab+")
            except Exception as e:
                print(e)
        except Exception as e:
            print(e)

        beacon_packet = logs.beacon_packet()
        file.write(bytearray(beacon_packet))
        file.close()
        
        tq.push(Message(10, beacon_packet))
        self.debug("Beacon task pushing to tq")
