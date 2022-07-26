"""
Python system check script for PyCubed satellite board
PyCubed Mini mainboard-v02 for Pocketqube Mission
Burnwire Deployment Test
* Author(s): Yashika Batra
"""

import time
from lib import pycubed as cubesat


def user_test():
    """
    All user interaction happens in this function
    Prompt users, get user inputs for voltage level and duration and return
    """

    wait_time = 10

    # conduct the test
    print("Initializing burnwire test...")
    print("You can test using a multimeter or fishing line.")
    print("If using a multimeter, please read the voltage between the" +
          "ground pin (GND) and burnwire pin on the -Z solar board.")

    # get user input for voltage level and duration
    voltage = float(input(
        "At what voltage do you want to run the burnwire IC? (up to 3.3V): "))
    burn_time = int(input(
        "For how long do you want to run the burnwire test? "))
    print("Test starting in", str(wait_time), "seconds.")
    time.sleep(wait_time)
    return voltage, burn_time


def burnwire_test(result_dict, burnnum):
    """
    All automation happens in this function
    Select burnwire and voltage level
    Process user test results and update the result dictionary accordingly
    """

    # get user input for voltage and duration
    voltage, burn_time = user_test()

    # calculate voltage level and conduct the test
    voltage_level = voltage / 3.3
    cubesat.burn(burn_num=str(burnnum), dutycycle=voltage_level,
                 duration=burn_time)

    # gather user input and return results
    print("Burnwire Test Complete")
    success_input = input("Did the test work as expected? (Y/N): ")
    success = False
    if success_input == "Y":
        success = True

    # process results
    result_key = 'Burnwire' + str(burnnum)
    result_val_string = ('Tested burnwire ' + str(burnnum) + ' at ' +
                         str(voltage) + ' V')
    result_dict[result_key] = (result_val_string, success)
    return result_dict


def run(hardware_dict, result_dict):
    """
    Check that the correct hardware is initialized and run tests
    """

    # if no Burn Wire 1 detected, update result dictionary
    if not hardware_dict['Burnwire1']:
        result_dict['Burnwire1'] = ('No burnwire 1 detected', False)
    else:  # Burn Wire 1 detected, run tests
        print("Starting Burnwire1 test...")
        burnwire_test(result_dict, 1)
        print("Burnwire1 Test complete.")
        print("")

    # if no Burn Wire 2 detected, update result dictionary
    if not hardware_dict['Burnwire2']:
        result_dict['Burnwire2'] = ('No burnwire 2 detected', False)
    else:  # Burn Wire 2 detected, run tests
        print("Starting Burnwire2 test...")
        burnwire_test(result_dict, 2)
        print("Burnwire2 Test complete.")
        print("")

    return result_dict
