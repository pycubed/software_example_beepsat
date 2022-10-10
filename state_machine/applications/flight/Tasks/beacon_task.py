# Transmit "Hello World" beacon

from lib.template_task import Task
import radio_utils.transmission_queue as tq
from radio_utils.message import Message
from pycubed import cubesat
from state_machine import state_machine
import struct

class task(Task):
    name = 'beacon'
    color = 'teal'

    async def main_task(self):
        """
        If you've attached a 433MHz antenna,
        set the above ANTENNA_ATTACHED variable to True
        to actually send the beacon packet
        """

        beacon_packet = self.beacon_packet()
        tq.push(Message(10, beacon_packet))
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
