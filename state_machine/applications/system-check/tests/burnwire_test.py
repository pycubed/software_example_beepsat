"""
Python system check script for PyCubed satellite board
PyCubed Mini mainboard-v02 for Pocketqube Mission
Burnwire Deployment Test
* Author(s): Yashika Batra
"""

from lib.pycubed import cubesat


def get_user_input():
    """
    Ask the user to type y/any key to start/cancel the test
    If y, return user inputs for voltage level and duration
    If any other key, return  None
    """

    # conduct the test
    print("Initializing burnwire test...")
    print("You can test using a multimeter or fishing line.")
    print("""If using a multimeter, please read the voltage between the ground pin
(GND) and burnwire pin on the -Z solar board.""")

    # get user input for voltage level and duration
    voltage = float(input("""At what voltage do you want to run the burnwire IC?
(number between 0 and 3.3): """))
    burn_time = int(input("How long do you want to run the burnwire test? (seconds): "))

    start_test = input("Type Y to start the test, any key to cancel: ")
    if start_test.lower() != "y":
        return None, None

    return voltage, burn_time


def burnwire_test(result_dict, burnnum):
    """
    Retrieve burnwire and voltage level from get_user_input() and run the test
    If None, update the result dictionary that the test was not run
    Else, process user inputted test results and update the result dictionary
    """

    # get user input for voltage and duration
    voltage, burn_time = get_user_input()

    # if voltage and burn_time are None, user entered "N" to cancel the test
    if voltage is None and burn_time is None:
        result_dict[f"Burnwire{burnnum}"] = ("Test was not run.", None)
        return result_dict

    # else, user entered "Y", calculate voltage level and conduct the test
    voltage_level = voltage / 3.3
    cubesat.burn(burn_num=str(burnnum), dutycycle=voltage_level,
                 duration=burn_time)

    # gather user input and return results
    print("Burnwire Test Complete")
    success_input = input("Did the test work as expected? (Y/N): ")
    success = False
    if success_input.lower() == "y":
        success = True

    # process results
    result_key = f"Burnwire {burnnum}"
    result_val_string = f"Tested burnwire {burnnum} at {voltage} V"
    result_dict[result_key] = (result_val_string, success)
    return result_dict


def run(hardware_dict, result_dict):
    """
    Check burnwire 1 and 2
    If initialized correctly, run test and update result dictionary
    through burnwire_test
    If not initialized, update result dictionary
    """

    # if no Burn Wire 1 detected, update result dictionary
    if not hardware_dict["Burnwire1"]:
        result_dict["Burnwire1"] = ("No burnwire 1 detected", None)
    else:  # Burn Wire 1 detected, run tests
        print("Starting Burnwire1 test...")
        burnwire_test(result_dict, 1)
        print("Burnwire1 Test complete.\n")

    # if no Burn Wire 2 detected, update result dictionary
    if not hardware_dict["Burnwire2"]:
        result_dict["Burnwire2"] = ("No burnwire 2 detected", None)
    else:  # Burn Wire 2 detected, run tests
        print("Starting Burnwire2 test...")
        burnwire_test(result_dict, 2)
        print("Burnwire2 Test complete.\n")

    return result_dict
