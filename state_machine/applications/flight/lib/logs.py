from pycubed import cubesat
from state_machine import state_machine
import struct
try:
    from ulab.numpy import array
except ImportError:
    from numpy import array


beacon_format = 'b' + 'f' * 11  # 1 char + 11 floats

def beacon_packet(task):
    """Creates a beacon packet containing the: CPU temp, IMU temp, gyro, acceleration, magnetic, and state byte.
    The state byte is the index of the current state in the alphabetically ordered state list.
    This data is packed into a c struct using `struct.pack`.

    If no IMU is attached it returns a packet of 0s.
    """
    if not cubesat.imu:
        task.debug('IMU not initialized')
        return bytes([0, 0, 0, 0, 0])

    cpu_temp = cubesat.temperature_cpu
    imu_temp = cubesat.temperature_imu
    gyro = cubesat.gyro
    acc = cubesat.acceleration
    mag = cubesat.magnetic
    state_byte = state_machine.states.index(state_machine.state)
    return struct.pack(beacon_format,
                       state_byte, cpu_temp, imu_temp,
                       gyro[0], gyro[1], gyro[2],
                       acc[0], acc[1], acc[2],
                       mag[0], mag[1], mag[2])

def unpack_beacon(bytes):
    """Unpacks the fields from the beacon packet packed by `beacon_packet`
    """

    (state_byte, cpu_temp, imu_temp,
     gyro0, gyro1, gyro2,
     acc0, acc1, acc2,
     mag0, mag1, mag2) = struct.unpack(beacon_format, bytes)

    gyro = array([gyro0, gyro1, gyro2])
    acc = array([acc0, acc1, acc2])
    mag = array([mag0, mag1, mag2])

    return state_byte, cpu_temp, imu_temp, gyro, acc, mag
