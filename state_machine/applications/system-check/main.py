"""
Python system check script for PyCubed satellite board
PyCubed Mini mainboard-v02 for Pocketqube Mission
* Author(s): Yashika Batra
"""

from lib.pycubed import pocketqube as cubesat
import tests
import tests.imu_test
import tests.radio_test
import tests.sun_sensor_test
import tests.coil_test
import tests.burnwire_test

"""
TODO:
run through files and documents for last check
fix string formatting
"""

# initialize hardware_dict and result_dict
hardware_dict = cubesat.hardware
result_dict = {
    'SD_Card_Logging': ('', False),
    'IMU_Acc_Still': ('', False),
    'IMU_Acc_Moving': ('', False),
    'IMU_Gyro_Still': ('', False),
    'IMU_Gyro_Turntable': ('', False),
    'IMU_Mag_Standalone': ('', False),
    'IMU_Mag_Magnet': ('', False),
    'IMU_Temp': ('', False),
    'Radio_Receive_Beacon': ('', False),
    'Radio_Send_Beacon': ('', False),
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
    'CoilDriverX_VoltTest': ('', False),
    'CoilDriverY_VoltTest': ('', False),
    'CoilDriverZ_VoltTest': ('', False),
    'Burnwire1_Volt1': ('', False),
    'Burnwire1_Volt2': ('', False),
    'Burnwire1_Volt3': ('', False),
    'Burnwire2_Volt1': ('', False),
    'Burnwire2_Volt2': ('', False),
    'Burnwire2_Volt3': ('', False)
}

# print acknowledgement that test has started
print("Running System Check...")
print("Initialization has concluded. Printing results...")
print("")
for entry in hardware_dict:
    print(str(entry.key), str(entry.val))
print("")

# check that solar boards are attached
run_sun_sensor = False
run_coil_driver = False
run_burnwire = False
solar_boards = input("Are the solar boards attached to the mainboard? (Y/N): ")
if solar_boards:
    run_sun_sensor = True
    run_coil_driver = True
    run_burnwire = True

# ask to test logging
logging_input = input("Would you like to test logging? (Y/N): ")
if logging_input == "Y":
    tests.logging_test.run(cubesat, hardware_dict, result_dict)

# ask to test imu
imu_input = input("Would you like to test the IMU sensors? (Y/N): ")
if imu_input == "Y":
    tests.imu_test.run(cubesat, hardware_dict, result_dict)

# ask to test radio
radio_input = input("Would you like to test the radio? (Y/N): ")
if radio_input == "Y":
    antenna_attached = input("Is an antenna attached to the radio? (Y/N): ")
    tests.radio_test.run(cubesat, hardware_dict, result_dict, antenna_attached)

# ask to test sun sensor
if run_sun_sensor:
    sun_sensor_input = input("Would you like to test the sun sensors? (Y/N): ")
    if sun_sensor_input == "Y":
        tests.sun_sensor_test.run(cubesat, hardware_dict, result_dict)

# ask to test coil driver
if run_coil_driver:
    coil_driver_input = input("Would you like to test the coil drivers? (Y/N): ")
    if coil_driver_input == "Y":
        tests.coil_test.run(cubesat, hardware_dict, result_dict)

# ask to test burnwire
if run_burnwire:
    burnwire_input = input("Would you like to test the burnwires? (Y/N): ")
    if burnwire_input == "Y":
        tests.burnwire_test.run(cubesat, hardware_dict, result_dict)

# end test and print results
print("")
print("Test has concluded. Printing results...")
print("")
for entry in hardware_dict:
    print(str(entry.key), str(entry.val))
print("")
