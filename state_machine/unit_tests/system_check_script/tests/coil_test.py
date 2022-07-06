import time

# voltage level constants; set between 0 and 1
# get these values from the hex values in doc
v1 = 0x0A
v2 = 0x15
v3 = 0x1F

def user_test(driver, coilidx, coilpin, vlevel):
    """
    All user interaction happens in this function
    Set wait times, change print statement and input formatting, etc.
    """

    # wait times
    multimeter_wait_time = 30
    driver_time = 30

    # formula in drv8830 docs:
    # https://www.ti.com/lit/ds/symlink/drv8830.pdf?ts=1657017752384&ref_url=https%253A%252F%252Fwww.ti.com%252Fproduct%252FDRV8830
    projected_voltage = 4 * 1.285 * int(vlevel) / 64

    # set up the test
    print("Testing Coil", str(coilidx), "for", projected_voltage, "volts.")
    print("Please retrieve a multimeter. Waiting", str(multimeter_wait_time), "seconds.")
    time.sleep(multimeter_wait_time)

    # figure out what pins we need to be reading
    # conduct the test
    print("Please read the voltage between the ground pin (GND) and coil pin (" + coilpin + "). \
        Waiting", str(driver_time), "seconds.")
    time.sleep(driver_time)

    # gather input and return results
    actual_voltage = float(input("Please enter the voltage you recorded: "))
    return projected_voltage, actual_voltage


def voltage_levelx(cubesat, result_dict, vnum, coilidx):
    """
    All automation happens in this function
    Select burnwire and voltage level
    Process user test results and update the result dictionary accordingly
    """

    # choose a coil driver or exit
    driver = 0
    if coilidx == 'X':
        driver = cubesat.drv_x
        coilpin = ""
    elif coilidx == 'Y':
        driver = cubesat.drv_y
        coilpin = ""
    elif coilidx == 'Z':
        driver = cubesat.drv_z
        coilpin = ""
    else:
        print("Not a valid coil.")
        exit()

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
        exit()

    # set string constant
    result_key = 'Coil' + str(coilidx) + '_Volt' + str(vlevel)

    # get user test result values, process and print results
    projected_voltage, actual_voltage = user_test(driver, coilidx, coilpin, vlevel)
    result_val_string = ('Coil ' + str(coilidx) + ' at voltage level ' +
                         str(vlevel) + 'returns ' + actual_voltage + ' volts')
    print(result_val_string)

    # update dictionary values based on user test result values
    if (abs(projected_voltage - actual_voltage) < 0.2):
        result_dict[result_key] = (result_val_string, True)
    else:
        result_dict[result_key] = (result_val_string, False)

    return result_dict


def run(cubesat, hardware_dict, result_dict):
    # if no Coil X detected, update result dictionary
    if not hardware_dict['Coil X']:
        result_dict['CoilX_Volt1'] = ('Cannot test Coil \
            X at ' + v1 + '; no Coil X detected', False)
        result_dict['CoilX_Volt2'] = ('Cannot test Coil \
            X at ' + v2 + '; no Coil X detected', False)
        result_dict['CoilX_Volt3'] = ('Cannot test Coil \
            X at ' + v3 + '; no Coil X detected', False)
    else:  # Coil X detected, run tests
        voltage_levelx(cubesat, result_dict, 1, 'X')
        voltage_levelx(cubesat, result_dict, 2, 'X')
        voltage_levelx(cubesat, result_dict, 3, 'X')

    # if no Coil Y detected, update result dictionary
    if not hardware_dict['Coil Y']:
        result_dict['CoilY_Volt1'] = ('Cannot test Coil \
            Y at ' + v1 + '; no Coil Y detected', False)
        result_dict['CoilY_Volt2'] = ('Cannot test Coil \
            Y at ' + v2 + '; no Coil Y detected', False)
        result_dict['CoilY_Volt3'] = ('Cannot test Coil \
            Y at ' + v3 + '; no Coil Y detected', False)
    else:  # Coil X detected, run tests
        voltage_levelx(cubesat, result_dict, 1, 'Y')
        voltage_levelx(cubesat, result_dict, 2, 'Y')
        voltage_levelx(cubesat, result_dict, 3, 'Y')

    # if no Coil Z detected, update result dictionary
    if not hardware_dict['Coil Z']:
        result_dict['CoilZ_Volt1'] = ('Cannot test Coil \
            Z at ' + v1 + '; no Coil Z detected', False)
        result_dict['CoilZ_Volt2'] = ('Cannot test Coil \
            Z at ' + v2 + '; no Coil Z detected', False)
        result_dict['CoilZ_Volt3'] = ('Cannot test Coil \
            Z at ' + v3 + '; no Coil Z detected', False)
    else:  # Coil X detected, run tests
        voltage_levelx(cubesat, result_dict, 1, 'Z')
        voltage_levelx(cubesat, result_dict, 2, 'Z')
        voltage_levelx(cubesat, result_dict, 3, 'Z')

    return result_dict
