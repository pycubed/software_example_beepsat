"""
Python system check script for PyCubed satellite board
PyCubed Mini mainboard-v02 for Pocketqube Mission
Torque Driver Test
* Author(s): Yashika Batra
"""

import time

# voltage level constants; set between 0 and 1
# get these values from the hex values in doc
v1 = 0x0A
v2 = 0x15
v3 = 0x1F

def user_test(driver, coilidx):
    """
    All user interaction happens in this function
    Set wait times, change print statement and input formatting, etc.
    """

    # wait times
    wait_time = 30
    driver_time = 10

    # formula in drv8830 docs:
    # https://www.ti.com/lit/ds/symlink/drv8830.pdf?ts=1657017752384&ref_url=https%253A%252F%252Fwww.ti.com%252Fproduct%252FDRV8830
    projected_voltage1 = 4 * 1.285 * int(v1) / 64
    projected_voltage2 = 4 * 1.285 * int(v2) / 64
    projected_voltage3 = 4 * 1.285 * int(v3) / 64

    # set up the test
    print("Testing Coil", str(coilidx), "for the following voltage levels: " +
          str(projected_voltage1) + ", " + str(projected_voltage2 + ", " +
          str(projected_voltage3)))
    print("Please retrieve a magnetometer. A cellphone app will also work. " +
          "Waiting", str(wait_time), "seconds.")
    time.sleep(wait_time)

    # figure out what pins we need to be reading
    # conduct the test
    print("Beginning the test now. Please note the magnetometer readings for the next",
          str(driver_time * 3), "seconds.")

    # test each voltage level
    driver.vout(v1)
    time.sleep(driver_time)
    driver.vout(v2)
    time.sleep(driver_time)
    driver.vout(v3)
    time.sleep(driver_time)

    # check user input
    print("Data Collection Complete")
    success = input("Did the magnetometer readings increase over the last " +
                    str(driver_time * 3) + " seconds? (Y/N): ")

    return success


def voltage_levelx(cubesat, result_dict, coilidx):
    """
    All automation happens in this function
    Select burnwire and voltage level
    Process user test results and update the result dictionary accordingly
    """

    # choose a coil driver or exit
    driver = 0
    if coilidx == 'X':
        driver = cubesat.drv_x
    elif coilidx == 'Y':
        driver = cubesat.drv_y
    elif coilidx == 'Z':
        driver = cubesat.drv_z
    else:
        print("Not a valid coil.")
        return result_dict

    # set string constant
    result_key = 'CoilDriver' + str(coilidx) + '_VoltTest'

    # get user test result values, process and print results
    result = user_test(driver, coilidx)
    result_val_string = ('Tested Coil Driver ' + str(coilidx) + ' at the following voltage levels: ' +
                         str(v1) + ', ' + str(v2) + ', ' + str(v3) + '.')
    if result:
        result_val_string += 'Magnetometer readings changed as expected with voltage levels.'
    else:
        result_val_string += 'Magnetometer readings did not change as expected.'

    # update result dictionary
    result_dict[result_key] = (result_val_string, result)
    return result_dict


def run(cubesat, hardware_dict, result_dict):
    # if no Coil X detected, update result dictionary
    if not hardware_dict['Coil X']:
        result_dict['CoilX_Volt1'] = ('Cannot test Coil X at ' +
                                      v1 + '; no Coil X detected', False)
        result_dict['CoilX_Volt2'] = ('Cannot test Coil X at ' +
                                      v2 + '; no Coil X detected', False)
        result_dict['CoilX_Volt3'] = ('Cannot test Coil X at ' +
                                      v3 + '; no Coil X detected', False)
    else:  # Coil X detected, run tests
        voltage_levelx(cubesat, result_dict, 'X')
        voltage_levelx(cubesat, result_dict, 'X')
        voltage_levelx(cubesat, result_dict, 'X')

    # if no Coil Y detected, update result dictionary
    if not hardware_dict['Coil Y']:
        result_dict['CoilY_Volt1'] = ('Cannot test Coil Y at ' +
                                      v1 + '; no Coil Y detected', False)
        result_dict['CoilY_Volt2'] = ('Cannot test Coil Y at ' +
                                      v2 + '; no Coil Y detected', False)
        result_dict['CoilY_Volt3'] = ('Cannot test Coil Y at ' +
                                      v3 + '; no Coil Y detected', False)
    else:  # Coil X detected, run tests
        voltage_levelx(cubesat, result_dict, 'Y')
        voltage_levelx(cubesat, result_dict, 'Y')
        voltage_levelx(cubesat, result_dict, 'Y')

    # if no Coil Z detected, update result dictionary
    if not hardware_dict['Coil Z']:
        result_dict['CoilZ_Volt1'] = ('Cannot test Coil Z at ' +
                                      v1 + '; no Coil Z detected', False)
        result_dict['CoilZ_Volt2'] = ('Cannot test Coil Z at ' +
                                      v2 + '; no Coil Z detected', False)
        result_dict['CoilZ_Volt3'] = ('Cannot test Coil Z at ' +
                                      v3 + '; no Coil Z detected', False)
    else:  # Coil X detected, run tests
        voltage_levelx(cubesat, result_dict, 'Z')
        voltage_levelx(cubesat, result_dict, 'Z')
        voltage_levelx(cubesat, result_dict, 'Z')

    return result_dict
