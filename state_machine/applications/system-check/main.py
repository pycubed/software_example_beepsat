"""
Python system check script for PyCubed satellite board
* Author(s): Yashika Batra
"""
# print acknowledgement that test has started
print("\n#################### S Y S T E M   C H E C K ####################\n")

from lib.pycubed import cubesat
import tests
import tests.i2c_scan
import tests.sd_test
# import tests.logging_infrastructure_test
import tests.imu_test
# import tests.radio_test
import tests.sun_sensor_test
import tests.coil_test
import tests.burnwire_test
import supervisor

supervisor.disable_autoreload()


# initialize hardware_dict and result_dict
result_dict = {
    "LoggingInfrastructure_Test": ("", False),
    "Basic_SDCard_Test": ("", False),
    "IMU_AccGravity": ("", False),
    "IMU_GyroStationary": ("", False),
    "IMU_GyroRotating": ("", False),
    "IMU_MagMagnet": ("", False),
    "IMU_Temp": ("", False),
    "Radio_ReceiveBeacon": ("", False),
    "Radio_SendBeacon": ("", False),
    "Sun-Y_Dark": ("", False),
    "Sun-Y_Light": ("", False),
    "Sun-Z_Dark": ("", False),
    "Sun-Z_Light": ("", False),
    "Sun-X_Dark": ("", False),
    "Sun-X_Light": ("", False),
    "Sun+Y_Dark": ("", False),
    "Sun+Y_Light": ("", False),
    "Sun+Z_Dark": ("", False),
    "Sun+Z_Light": ("", False),
    "Sun+X_Dark": ("", False),
    "Sun+X_Light": ("", False),
    "CoilDriverX": ("", False),
    "CoilDriverY": ("", False),
    "CoilDriverZ": ("", False),
    "Burnwire1": ("", False),
}

# complete an i2c scan: print all devices connected to each i2c bus
tests.i2c_scan.run()

# test sd card
tests.sd_test.run(result_dict)

# test logging infrastructure
# tests.logging_infrastructure_test.run(result_dict)

# test imu
tests.imu_test.run(result_dict)

# test sun sensor
tests.sun_sensor_test.run(result_dict)

# test coil driver
tests.coil_test.run(result_dict)

# ask to test burnwire
burnwire_input = input("Type Y to start burnwire test, any key to cancel: ")
if burnwire_input.lower() == "y":
    tests.burnwire_test.run(result_dict)
else:
    result_dict["Burnwire1"] = ("Test was not run.", None)
    result_dict["Burnwire2"] = ("Test was not run.", None)

'''
# ask to test radio
radio_input = input("Type Y to start the radio test, any key to cancel: ")
if radio_input.lower() == "y":
    antenna_attached = input("Is an antenna attached to the radio? (Y/N): ")
    tests.radio_test.run(hardware_dict, result_dict, antenna_attached)
else:
    result_dict["Radio_ReceiveBeacon"] = ("Test was not run.", None)
    result_dict["Radio_SendBeacon"] = ("Test was not run.", None)
'''

# print test results; failed tests first, and then passed tests
print("\nTest has concluded. Printing results...\n")

print("Tests not run:")
for entry in result_dict.items():
    if entry[1][1] is None:
        # entry[1][0] is the string portion of the tuple
        print(f"{entry[0]}")
print("")

print("Failed tests:")
for entry in result_dict.items():
    # if the test failed
    if entry[1][1] is not None and not entry[1][1]:
        # entry[1][0] is the string portion of the tuple
        print(f"{entry[0]}: {entry[1][0]}")
print("")

print("Passed tests:")
for entry in result_dict.items():
    # if the test passed
    if entry[1][1] is not None and entry[1][1]:
        # entry[1][0] is the string portion of the tuple
        print(f"{entry[0]}: {entry[1][0]}")
print("")
