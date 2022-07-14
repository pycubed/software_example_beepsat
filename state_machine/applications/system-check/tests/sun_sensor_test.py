"""
Python system check script for PyCubed satellite board
PyCubed Mini mainboard-v02 for Pocketqube Mission
Sun Sensor Test
* Author(s): Yashika Batra
"""

import time

def user_test(sun_sensor, sensoridx, light_dark):
    """
    All user interaction happens in this function
    Set wait times, change print statement and input formatting, etc.
    """

    wait_time = 30

    print("Testing Sun Sensor", str(sensoridx), "in the", light_dark)

    if light_dark == "Light":
        print("Please turn on the lights. Waiting", wait_time, "seconds.")
    elif light_dark == "Dark":
        print("Please remove all nearby light sources or cover the sensor. " +
              "Waiting", wait_time, "seconds.")

    time.sleep(wait_time)
    print("Collecting sensor data...")
    res = sun_sensor._compute_lux()
    print("Data collection complete.")
    return res


def test_sensorx(cubesat, result_dict, sensoridx, light_dark):
    """
    All automation happens in this function
    Select burnwire and voltage level
    Process user test results and update the result dictionary accordingly
    """

    sun_sensor = 0
    result_key = ''
    if sensoridx == '-Y':
        sun_sensor = cubesat.sun_yn
        result_key = 'Sun_MinusY_'
    if sensoridx == '-Z':
        sun_sensor = cubesat.sun_zn
        result_key = 'Sun_MinusX_'
    if sensoridx == '-X':
        sun_sensor = cubesat.sun_xn
        result_key = 'Sun_MinusX_'
    if sensoridx == '+Y':
        sun_sensor = cubesat.sun_yp
        result_key = 'Sun_PlusY_'
    if sensoridx == '+Z':
        sun_sensor = cubesat.sun_zp
        result_key = 'Sun_PlusZ_'
    if sensoridx == '+X':
        sun_sensor = cubesat.sun_xp
        result_key = 'Sun_PlusX_'

    lux = user_test(sun_sensor, sensoridx, light_dark)

    # find result key and result value strings
    result_key = result_key + light_dark
    if lux:
        result_val_string = ("Testing Sun Sensor " + sensoridx + " in the " +
                             light_dark + "resulted in a lux value of " + str(lux))
    else:
        result_val_string = ("No lux value returned; lux is None.")

    if light_dark == "Light":
        # test result values and update result_dict
        if lux is not None and lux >= 100:  # 100 is enough to illuminate small room
            result_dict[result_key] = (result_val_string, True)
        else:
            result_dict[result_key] = (result_val_string, False)

    elif light_dark == 'Dark':
        # test result values and update result_dict
        if lux is not None and lux < 50:  # 50 is about equal to low indoor light
            result_dict[result_key] = (result_val_string, True)
        else:
            result_dict[result_key] = (result_val_string, False)

    return result_dict


def run(cubesat, hardware_dict, result_dict):
    # if no Sun Sensor -Y detected, update result dictionary
    if not hardware_dict['Sun -Y']:
        result_dict['Sun_MinusY_Dark'] = (
            'Cannot test sun sensor -Y in light; no sun sensor -Y detected', False)
        result_dict['Sun_MinusY_Dark'] = (
            'Cannot test sun sensor -Y in dark; no sun sensor -Y detected', False)
    else:  # Sun Sensor -Y detected, run tests
        test_sensorx(cubesat, result_dict, '-Y', 'Light')
        test_sensorx(cubesat, result_dict, '-Y', 'Dark')

    # if no Sun Sensor -Z detected, update result dictionary
    if not hardware_dict['Sun -Z']:
        result_dict['Sun_MinusZ_Dark'] = (
            'Cannot test sun sensor -Z in light; no sun sensor -Z detected', False)
        result_dict['Sun_MinusZ_Dark'] = (
            'Cannot test sun sensor -Z in dark; no sun sensor -Z detected', False)
    else:  # Sun Sensor -Z detected, run tests
        test_sensorx(cubesat, result_dict, '-Z', 'Light')
        test_sensorx(cubesat, result_dict, '-Z', 'Dark')

    # if no Sun Sensor -X detected, update result dictionary
    if not hardware_dict['Sun -X']:
        result_dict['Sun_MinusX_Dark'] = (
            'Cannot test sun sensor -X in light; no sun sensor -X detected', False)
        result_dict['Sun_MinusX_Dark'] = (
            'Cannot test sun sensor -X in dark; no sun sensor -X detected', False)
    else:  # Sun Sensor -X detected, run tests
        test_sensorx(cubesat, result_dict, '-X', 'Light')
        test_sensorx(cubesat, result_dict, '-X', 'Dark')

    # if no Sun Sensor +Y detected, update result dictionary
    if not hardware_dict['Sun +Y']:
        result_dict['Sun_PlusY_Dark'] = (
            'Cannot test sun sensor +Y in light; no sun sensor +Y detected', False)
        result_dict['Sun_PlusY_Dark'] = (
            'Cannot test sun sensor +Y in dark; no sun sensor +Y detected', False)
    else:  # Sun Sensor +Y detected, run tests
        test_sensorx(cubesat, result_dict, '+Y', 'Light')
        test_sensorx(cubesat, result_dict, '+Y', 'Dark')

    # if no Sun Sensor +Z detected, update result dictionary
    if not hardware_dict['Sun +Z']:
        result_dict['Sun_PlusZ_Dark'] = (
            'Cannot test sun sensor +Z in light; no sun sensor +Z detected', False)
        result_dict['Sun_PlusZ_Dark'] = (
            'Cannot test sun sensor +Z in dark; no sun sensor +Z detected', False)
    else:  # Sun Sensor +Z detected, run tests
        test_sensorx(cubesat, result_dict, '+Z', 'Light')
        test_sensorx(cubesat, result_dict, '+Z', 'Dark')

    # if no Sun Sensor +X detected, update result dictionary
    if not hardware_dict['Sun +X']:
        result_dict['Sun_PlusX_Dark'] = (
            'Cannot test sun sensor +X in light; no sun sensor +X detected', False)
        result_dict['Sun_PlusX_Dark'] = (
            'Cannot test sun sensor +X in dark; no sun sensor +X detected', False)
    else:  # Sun Sensor +X detected, run tests
        test_sensorx(cubesat, result_dict, '+X', 'Light')
        test_sensorx(cubesat, result_dict, '+X', 'Dark')

    return result_dict
