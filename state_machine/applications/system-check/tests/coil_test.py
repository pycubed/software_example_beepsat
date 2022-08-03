"""
Python system check script for PyCubed satellite board
PyCubed Mini mainboard-v02 for Pocketqube Mission
Torque Driver Test
* Author(s): Yashika Batra
"""

import time
from lib import pycubed as cubesat
from ulab.numpy.linalg import norm

# voltage level constants; set between -1 and 1
v1 = 0.25
v2 = 0.5
v3 = 0.75

# find projected voltage: vlevel * max voltage
projected_voltage1 = v1 * 5.06
projected_voltage2 = v2 * 5.06
projected_voltage3 = v3 * 5.06


def test_voltage_levels(coil_index):
    """
    All user interaction happens in this function
    Set wait times, prompt user, collect magnetometer data for
    different voltage levels
    """

    # wait times
    wait_time = 3
    driver_time = 3

    # set up the test
    print(f'Testing Coil Driver {coil_index} for the following voltage ' +
          f'levels: {projected_voltage1}, {projected_voltage2}, ' +
          f'{projected_voltage3}.')
    print(f"Waiting {wait_time} seconds.")
    time.sleep(wait_time)

    # conduct the test
    start_test = input("Type Y to start the test, N to cancel: ")
    if start_test.lower() == "n":
        return None

    # else, test each voltage level
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
    mag_total1 = norm(mag_reading1)
    mag_total2 = norm(mag_reading2)
    mag_total3 = norm(mag_reading3)

    # if magnetometer readings are increasing over time, return true
    result_val_bool = (mag_total3 > mag_total2 and mag_total2 > mag_total1)
    if not result_val_bool:
        print("Magnetometer results should have been increasing but were" +
              f"not. reading 1: {mag_total1}, reading 2: {mag_total2}," +
              f"reading 3: {mag_total3}")
    return result_val_bool


def coil_test(result_dict, coil_index):
    """
    All automation happens in this function
    Process user test results and update the result dictionary accordingly
    """

    # set string constant
    result_key = f"CoilDriver{coil_index}"

    # get user test result values, process and print results
    result = test_voltage_levels(coil_index)
    if result is None:
        result_dict[result_key] = (f"{result_key} not tested.", result)

    result_val_string = (f'Tested Coil Driver {coil_index} at the following' +
                         f'voltage levels: {projected_voltage1}, ' +
                         f'{projected_voltage2}, {projected_voltage3}.')

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
        coil_test(result_dict, 'X')
        print("Coil Driver X Test complete.\n")

    # if no Coil Y detected, update result dictionary
    if not hardware_dict['CoilDriverY']:
        result_dict['CoilDriverY'] = ('No Coil Driver Y detected', False)
    else:  # Coil Y detected, run tests
        print("Starting Coil Driver Y test...")
        coil_test(result_dict, 'Y')
        print("Coil Driver Y Test complete.\n")

    # if no Coil Z detected, update result dictionary
    if not hardware_dict['CoilDriverZ']:
        result_dict['CoilDriverZ'] = ('No Coil Driver Z detected', False)
    else:  # Coil Z detected, run tests
        print("Starting Coil Driver Z test...")
        coil_test(result_dict, 'Z')
        print("Coil Driver Z Test complete.\n")

    return result_dict
