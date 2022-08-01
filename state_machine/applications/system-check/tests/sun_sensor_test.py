"""
Python system check script for PyCubed satellite board
PyCubed Mini mainboard-v02 for Pocketqube Mission
Sun Sensor Test
* Author(s): Yashika Batra
"""

import time
from lib import pycubed as cubesat


def lux(sun_sensor_index):
    """ Return the lux reading for a given sun sensor """
    if sun_sensor_index == "-Y":
        return cubesat._cubesat.sun_yn.lux
    elif sun_sensor_index == "-Z":
        return cubesat._cubesat.sun_zn.lux
    elif sun_sensor_index == "-X":
        return cubesat._cubesat.sun_xn.lux
    elif sun_sensor_index == "+Y":
        return cubesat._cubesat.sun_yp.lux
    elif sun_sensor_index == "+Z":
        return cubesat._cubesat.sun_zp.lux
    elif sun_sensor_index == "+X":
        return cubesat._cubesat.sun_xp.lux
    else:
        print(sun_sensor_index, "is not a defined sun sensor.")
        return


def user_test(sensor_index, light_dark):
    """
    All user interaction happens in this function
    Set wait times, prompt the user and collect lux data
    """

    wait_time = 3

    print("Testing Sun Sensor {sensor_index} in the {light_dark}.")

    if light_dark == "Light":
        print("Please turn on the lights. Waiting {wait_time} seconds.")
    elif light_dark == "Dark":
        print("Please remove all nearby light sources or cover the sensor. " +
              "Waiting {wait_time} seconds.")

    time.sleep(wait_time)
    print("Collecting sensor data...")
    lux_val = lux(sensor_index)
    print("Data collection complete.")
    return lux_val


def test_sensorx(result_dict, sensor_index, light_dark):
    """
    All automation happens in this function
    Process user test results and update the result dictionary accordingly
    """

    # get lux value from the user test
    lux_val = user_test(sensor_index, light_dark)

    # find result key and result value strings
    result_key = 'Sun' + sensor_index + '_' + light_dark
    if lux_val:
        result_val_string = ("Testing Sun Sensor {sensor_index} in the" +
                             "{light_dark} resulted in a lux value of" +
                             "{lux_val}")
    else:
        result_val_string = ("No lux value returned; lux is None.")

    if light_dark == "Light":
        # 100 is enough to illuminate small room
        result_val_bool = lux_val is not None and lux_val >= 100
        result_dict[result_key] = (result_val_string, result_val_bool)

    elif light_dark == 'Dark':
        # 50 is about equal to low indoor light
        result_val_bool = lux_val is not None and lux_val < 50
        result_dict[result_key] = (result_val_string, result_val_bool)

    return result_dict


def run(hardware_dict, result_dict):
    """
    Check that the correct hardware is initialized and run tests
    """

    # if no Sun Sensor -Y detected, update result dictionary
    if not hardware_dict['Sun-Y']:
        result_dict['Sun-Y_Light'] = (
            'Cannot test sun sensor -Y in light; no sun sensor -Y detected',
            False)
        result_dict['Sun-Y_Dark'] = (
            'Cannot test sun sensor -Y in dark; no sun sensor -Y detected',
            False)
    else:  # Sun Sensor -Y detected, run tests
        print("Starting Sun Sensor -Y test...")
        test_sensorx(result_dict, '-Y', 'Light')
        test_sensorx(result_dict, '-Y', 'Dark')
        print("Sun Sensor -Y test complete.\n")

    # if no Sun Sensor -Z detected, update result dictionary
    if not hardware_dict['Sun-Z']:
        result_dict['Sun-Z_Light'] = (
            'Cannot test sun sensor -Z in light; no sun sensor -Z detected',
            False)
        result_dict['Sun-Z_Dark'] = (
            'Cannot test sun sensor -Z in dark; no sun sensor -Z detected',
            False)
    else:  # Sun Sensor -Z detected, run tests
        print("Starting Sun Sensor -Z test...")
        test_sensorx(result_dict, '-Z', 'Light')
        test_sensorx(result_dict, '-Z', 'Dark')
        print("Sun Sensor -Z test complete.\n")

    # if no Sun Sensor -X detected, update result dictionary
    if not hardware_dict['Sun-X']:
        result_dict['Sun-X_Light'] = (
            'Cannot test sun sensor -X in light; no sun sensor -X detected',
            False)
        result_dict['Sun-X_Dark'] = (
            'Cannot test sun sensor -X in dark; no sun sensor -X detected',
            False)
    else:  # Sun Sensor -X detected, run tests
        print("Starting Sun Sensor -X test...")
        test_sensorx(result_dict, '-X', 'Light')
        test_sensorx(result_dict, '-X', 'Dark')
        print("Sun Sensor -X test complete.\n")

    # if no Sun Sensor +Y detected, update result dictionary
    if not hardware_dict['Sun+Y']:
        result_dict['Sun+Y_Light'] = (
            'Cannot test sun sensor +Y in light; no sun sensor +Y detected',
            False)
        result_dict['Sun+Y_Dark'] = (
            'Cannot test sun sensor +Y in dark; no sun sensor +Y detected',
            False)
    else:  # Sun Sensor +Y detected, run tests
        print("Starting Sun Sensor +Y test...")
        test_sensorx(result_dict, '+Y', 'Light')
        test_sensorx(result_dict, '+Y', 'Dark')
        print("Sun Sensor +Y test complete.\n")

    # if no Sun Sensor +Z detected, update result dictionary
    if not hardware_dict['Sun+Z']:
        result_dict['Sun+Z_Light'] = (
            'Cannot test sun sensor +Z in light; no sun sensor +Z detected',
            False)
        result_dict['Sun+Z_Dark'] = (
            'Cannot test sun sensor +Z in dark; no sun sensor +Z detected',
            False)
    else:  # Sun Sensor +Z detected, run tests
        print("Starting Sun Sensor +Z test...")
        test_sensorx(result_dict, '+Z', 'Light')
        test_sensorx(result_dict, '+Z', 'Dark')
        print("Sun Sensor +Z test complete.\n")

    # if no Sun Sensor +X detected, update result dictionary
    if not hardware_dict['Sun+X']:
        result_dict['Sun+X_Light'] = (
            'Cannot test sun sensor +X in light; no sun sensor +X detected',
            False)
        result_dict['Sun+X_Dark'] = (
            'Cannot test sun sensor +X in dark; no sun sensor +X detected',
            False)
    else:  # Sun Sensor +X detected, run tests
        print("Starting Sun Sensor +X test...")
        test_sensorx(result_dict, '+X', 'Light')
        test_sensorx(result_dict, '+X', 'Dark')
        print("Sun Sensor +X test complete.\n")

    return result_dict
