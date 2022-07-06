from lib.pycubed import pocketqube as cubesat
import tests

hardware_dict = cubesat.hardware
result_dict = {
    'SD_Card_Logging': ('', False),
    'IMU_Acc_Still': ('', False),
    'IMU_Acc_Moving': ('', False),
    'IMU_Gyro_Still': ('', False),
    'IMU_Gyro_Turntable': ('', False),
    'IMU_Mag_Magnet': ('', False),
    'IMU_Temp': ('', False),
    'Radio_Send_Beacon': ('', False),
    'Radio_Receive_Beacon': ('', False),
    'Sun_MinusY_Dark': ('', False),
    'Sun_MinusY_Light': ('', False),
    'Sun_MinusZ_Dark': ('', False),
    'Sun_MinusZ_Light': ('', False),
    'Sun_MinusX_Dark': ('', False),
    'Sun_MinusX_Light': ('', False),
    'Sun_PlusY_Dark': ('', False),
    'Sun_PlusY_Light': ('', False),
    'Sun_PlusZ_Dark': ('', False),
    'Sun_PlusZ_Light': ('', False),
    'Sun_PlusX_Dark': ('', False),
    'Sun_PlusX_Light': ('', False),
    'CoilX_Volt1': ('', False),
    'CoilX_Volt2': ('', False),
    'CoilX_Volt3': ('', False),
    'CoilY_Volt1': ('', False),
    'CoilY_Volt2': ('', False),
    'CoilY_Volt3': ('', False),
    'CoilZ_Volt1': ('', False),
    'CoilZ_Volt2': ('', False),
    'CoilZ_Volt3': ('', False),
    'Burnwire1_Volt1': ('', False),
    'Burnwire1_Volt2': ('', False),
    'Burnwire1_Volt3': ('', False),
    'Burnwire2_Volt1': ('', False),
    'Burnwire2_Volt2': ('', False),
    'Burnwire2_Volt3': ('', False)
}

tests.logging_test.run(cubesat, hardware_dict, result_dict)
tests.imu_test.run(cubesat, hardware_dict, result_dict)
tests.radio_test.run(cubesat, hardware_dict, result_dict)
tests.sun_sensor_test.run(cubesat, hardware_dict, result_dict)
tests.coil_test.run(cubesat, hardware_dict, result_dict)
tests.burnwire_test.run(cubesat, hardware_dict, result_dict)
