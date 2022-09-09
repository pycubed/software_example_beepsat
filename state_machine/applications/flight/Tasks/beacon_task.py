# Transmit "Hello World" beacon

from lib.template_task import Task
import radio_utils.transmission_queue as tq
from radio_utils.message import Message
from radio_utils.naive import NaiveMessage
from pycubed import cubesat
from state_machine import state_machine
import struct

msg = """"Did you ever hear the tragedy of Darth Plagueis the Wise?"
"No."
"I thought not. It's not a story the Jedi would tell you.
It's a Sith legend. Darth Plagueis...
was a Dark Lord of the Sith so powerful and so wise, he could use the Force to influence the midi-chlorians...
to create... life. He had such a knowledge of the dark side, he could even keep the ones he cared about... from dying."
"He could actually... save people from death?"
"The dark side of the Force is a pathway to many abilities... some consider to be unnatural."
"Wh- What happened to him?"
"He became so powerful, the only thing he was afraid of was... losing his power. Which eventually, of course, he did.
Unfortunately, he taught his apprentice everything he knew.
Then his apprentice killed him in his sleep. It's ironic. He could save others from death, but not himself."
"Is it possible to learn this power?"
"Not from a Jedi."
--Darth Sidious and Anakin Skywalker"""

class task(Task):
    name = 'beacon'
    color = 'teal'
    first_time = True

    async def main_task(self):
        """
        If you've attached a 433MHz antenna,
        set the above ANTENNA_ATTACHED variable to True
        to actually send the beacon packet
        """

        beacon_packet = self.beacon_packet()
        tq.push(Message(10, beacon_packet))
        if self.first_time:
            self.first_time = False
            self.debug("Pushing the large msg to tq")
            tq.push(NaiveMessage(1, msg))
        self.debug("Beacon task pushing to tq")

    def beacon_packet(self):
        if not cubesat.imu:
            self.debug('IMU not initialized')
            return bytes([0, 0, 0, 0, 0])

        cpu_temp = cubesat.temperature_cpu
        imu_temp = cubesat.temperature_imu
        gyro = cubesat.gyro
        acc = cubesat.acceleration
        mag = cubesat.magnetic
        state_byte = state_machine.states.index(state_machine.state)
        print(f'CPU temp: {cpu_temp}')
        print(f'IMU temp: {imu_temp}')
        print(f'Gyro: {gyro}')
        print(f'Acceleration: {acc}')
        print(f'Magnetic: {mag}')
        print(f'State: {state_machine.state} [{state_byte}]')
        format = 'b' + 'f' * 11  # 1 char + 11 floats
        return struct.pack(format,
                           state_byte, cpu_temp, imu_temp,
                           gyro[0], gyro[1], gyro[2],
                           acc[0], acc[1], acc[2],
                           mag[0], mag[1], mag[2])
