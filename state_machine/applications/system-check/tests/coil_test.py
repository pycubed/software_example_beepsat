"""
Python system check script for PyCubed satellite board
PyCubed Mini mainboard-v02 for Pocketqube Mission
Torque Driver Test
* Author(s): Yashika Batra
"""

import time
from lib import pycubed as cubesat
from math import sqrt

# voltage level constants; set between -1 and 1
v1 = 0.25
v2 = 0.5
v3 = 0.75

# find projected voltage: vlevel * max voltage
projected_voltage1 = v1 * 5.06
projected_voltage2 = v2 * 5.06
projected_voltage3 = v3 * 5.06


def user_test(coil_index):
    """
    All user interaction happens in this function
    Set wait times, prompt user, collect magnetometer data for
    different voltage levels
    """

    # wait times
    wait_time = 3
    driver_time = 3

    # set up the test
    print("Testing Coil", str(coil_index),
          "for the following voltage levels: " + str(projected_voltage1) +
          ", " + str(projected_voltage2) + ", " + str(projected_voltage3))
    print("Waiting", str(wait_time), "seconds.")
    time.sleep(wait_time)

    # conduct the test
    print("Beginning the test now. Testing for", str(driver_time * 3),
          "seconds.")

    # test each voltage level
    cubesat.coildriver_vout(coil_index, projected_voltage1)
    time.sleep(driver_time)
    mag_reading1 = cubesat.magnetic()

    cubesat.coildriver_vout(coil_index, projected_voltage2)
    time.sleep(driver_time)
    mag_reading2 = cubesat.magnetic()

    cubesat.coildriver_vout(coil_index, projected_voltage3)
    time.sleep(driver_time)
    mag_reading3 = cubesat.magnetic()

    # calculate total magnetic reading
    print("Data Collection Complete")
    mag_total1 = sqrt(
        mag_reading1[0] ** 2 + mag_reading1[1] ** 2 + mag_reading1[2] ** 2)
    mag_total2 = sqrt(
        mag_reading2[0] ** 2 + mag_reading2[1] ** 2 + mag_reading2[2] ** 2)
    mag_total3 = sqrt(
        mag_reading3[0] ** 2 + mag_reading3[1] ** 2 + mag_reading3[2] ** 2)

    # if magnetometer readings are increasing over time, return true
    return (mag_total3 > mag_total2 and mag_total2 > mag_total1)


def voltage_levelx(result_dict, coil_index):
    """
    All automation happens in this function
    Process user test results and update the result dictionary accordingly
    """

    # set string constant
    result_key = 'CoilDriver' + str(coil_index)

    # get user test result values, process and print results
    result = user_test(coil_index)
    result_val_string = ('Tested Coil Driver ' + str(coil_index) +
                         ' at the following voltage levels: ' +
                         str(projected_voltage1) + ', ' +
                         str(projected_voltage2) + ', ' +
                         str(projected_voltage3) + '.')
    if result:
        result_val_string += 'Magnetometer readings changed as expected.'
    else:
        result_val_string += ('Magnetometer readings did not change as' +
                              'expected.')

    # update result dictionary
    result_dict[result_key] = (result_val_string, result)
    return result_dict


def run(hardware_dict, result_dict):
    """
    Check that the correct hardware is initialized and run tests
    """

    # if no Coil X detected, update result dictionary
    if not hardware_dict['CoilDriverX']:
        result_dict['CoilDriverX'] = ('No Coil Driver X detected', False)
    else:  # Coil X detected, run tests
        print("Starting Coil Driver X test...")
        voltage_levelx(result_dict, 'X')
        print("Coil Driver X Test complete.")
        print("")

    # if no Coil Y detected, update result dictionary
    if not hardware_dict['CoilDriverY']:
        result_dict['CoilDriverY'] = ('No Coil Driver Y detected', False)
    else:  # Coil X detected, run tests
        print("Starting Coil Driver Y test...")
        voltage_levelx(result_dict, 'Y')
        print("Coil Driver Y Test complete.")
        print("")

    # if no Coil Z detected, update result dictionary
    if not hardware_dict['CoilDriverZ']:
        result_dict['CoilDriverZ'] = ('No Coil Driver Z detected', False)
    else:  # Coil X detected, run tests
        print("Starting Coil Driver Z test...")
        voltage_levelx(result_dict, 'Z')
        print("Coil Driver Z Test complete.")
        print("")

    return result_dict
