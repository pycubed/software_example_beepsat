"""
Python system check script for PyCubed satellite board
PyCubed Mini mainboard-v02 for Pocketqube Mission
Burnwire Deployment Test
* Author(s): Yashika Batra
"""

import time

# voltage level constants; set between 0 and 1
v1 = 0.25
v2 = 0.5
v3 = 0.75

def user_test(burnnum, burnwire, vlevel):
    """
    All user interaction happens in this function
    Set wait times, change print statement and input formatting, etc.
    """

    # wait times
    multimeter_wait_time = 30
    burn_time = 30

    # other constants
    projected_voltage = vlevel * 3.3
    dutycycle = int((vlevel / 100) * (0xFFFF))

    # set up the test
    print("Testing Burn Wire IC", str(burnnum), "for", projected_voltage, "volts.")
    print("Please retrieve a multimeter. Waiting", str(multimeter_wait_time), "seconds.")
    time.sleep(multimeter_wait_time)

    # conduct the test
    print("Please read the voltage between the ground pin (GND) and burnwire pin on the -Z solar board.")
    print("Waiting", str(burn_time), "seconds.")
    burnwire.duty_cycle = dutycycle
    time.sleep(burn_time)
    burnwire.duty_cycle = 0

    # gather input and return results
    print("Burnwire Test Complete")
    actual_voltage = float(input("Please enter the voltage you recorded: "))
    return projected_voltage, actual_voltage


def voltage_levelx(cubesat, result_dict, vnum, burnnum):
    """
    All automation happens in this function
    Select burnwire and voltage level
    Process user test results and update the result dictionary accordingly
    """

    # choose a burnwire or exit
    burnwire = 0
    if burnnum == 1:
        burnwire = cubesat.burnwire1
    elif burnnum == 2:
        burnwire = cubesat.burnwire2
    else:
        print("Not a valid burnwire.")
        return result_dict

    # choose a voltage level or exit
    vlevel = 0
    if vnum == 1:
        vlevel = v1
    elif vnum == 2:
        vlevel = v2
    elif vnum == 3:
        vlevel = v3
    else:
        print("Not a valid voltage level option.")
        return result_dict

    # set string constant
    result_key = 'Burnwire' + str(burnnum) + '_Volt' + str(vlevel)

    # get user test result values, process and print results
    projected_voltage, actual_voltage = user_test(burnnum, burnwire, vlevel)
    result_val_string = ('Burnwire ' + str(burnnum) + ' at voltage level ' +
                         str(vlevel) + 'returns ' + actual_voltage + ' volts')
    print(result_val_string)

    # update dictionary values based on user test result values
    if (abs(projected_voltage - actual_voltage) < 0.2):
        result_dict[result_key] = (result_val_string, True)
    else:
        result_dict[result_key] = (result_val_string, False)

    return result_dict


def run(cubesat, hardware_dict, result_dict):
    # if no Burn Wire 1 detected, update result dictionary
    if not hardware_dict['Burn Wire 1']:
        result_dict['Burnwire1_Volt1'] = ('Cannot test burnwire 1 at ' +
                                          v1 + '; no burnwire 1 detected', False)
        result_dict['Burnwire1_Volt2'] = ('Cannot test burnwire 1 at ' +
                                          v2 + '; no burnwire 1 detected', False)
        result_dict['Burnwire1_Volt3'] = ('Cannot test burnwire 1 at ' +
                                          v3 + '; no burnwire 1 detected', False)
    else:  # Burn Wire 1 detected, run tests
        voltage_levelx(cubesat, result_dict, 1, 1)
        voltage_levelx(cubesat, result_dict, 2, 1)
        voltage_levelx(cubesat, result_dict, 3, 1)

    # if no Burn Wire 2 detected, update result dictionary
    if not hardware_dict['Burn Wire 2']:
        result_dict['Burnwire1_Volt1'] = ('Cannot test burnwire 2 at ' + v1 +
                                          '; burnwire 2 integrated circuit is not set up', False)
        result_dict['Burnwire1_Volt2'] = ('Cannot test burnwire 2 at ' + v2 +
                                          '; burnwire 2 integrated circuit is not set up', False)
        result_dict['Burnwire1_Volt3'] = ('Cannot test burnwire 2 at ' + v3 +
                                          '; burnwire 2 integrated circuit is not set up', False)
    else:  # Burn Wire 2 detected, run tests
        voltage_levelx(cubesat, result_dict, 1, 2)
        voltage_levelx(cubesat, result_dict, 2, 2)
        voltage_levelx(cubesat, result_dict, 3, 2)

    return result_dict
