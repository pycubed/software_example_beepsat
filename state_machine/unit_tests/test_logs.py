import unittest
import sys
from numpy import testing, array

sys.path.insert(0, './state_machine/drivers/emulation')
sys.path.insert(0, './state_machine/drivers/emulation/lib')
sys.path.insert(0, './state_machine/applications/flight')
sys.path.insert(0, './state_machine/frame')

from lib.logs import beacon_packet, unpack_beacon
from pycubed import cubesat
from state_machine import state_machine
from lib.template_task import Task

class TestLogs(unittest.TestCase):

    def test(self):

        task = Task()

        accel_in = array([1.0, 2.0, 3.0])
        mag_in = array([4.0, 3.0, 1.0])
        gyro_in = array([-42.0, 0.1, 7.0])

        cpu_temp_in = 77
        imu_temp_in = 22

        cubesat._accel = accel_in
        cubesat._mag = mag_in
        cubesat._gyro = gyro_in
        cubesat._cpu_temp = cpu_temp_in
        cubesat._imu_temperature = imu_temp_in

        state_machine.states = [1, 2, 3, 4]
        state_machine.state = 2
        state_in = state_machine.states.index(state_machine.state)

        pkt = beacon_packet(task)

        state_out, cpu_temp_out, imu_temp_out, gyro_out, accel_out, mag_out = unpack_beacon(pkt)

        self.assertEqual(state_in, state_out)
        self.assertEqual(cpu_temp_in, cpu_temp_out)
        self.assertEqual(imu_temp_in, imu_temp_out)
        testing.assert_array_almost_equal(accel_in, accel_out)
        testing.assert_array_almost_equal(gyro_in, gyro_out)
        testing.assert_array_almost_equal(mag_in, mag_out)
