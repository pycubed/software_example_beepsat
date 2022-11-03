"""
Python system check script for PyCubed satellite board
PyCubed Mini mainboard-v02 for Pocketqube Mission
Sun Sensor Test
* Author(s): Yashika Batra
"""

from lib.pycubed import cubesat


def lux(sun_sensor_index):
    """
    Return the lux reading for a given sun sensor
    """
    if sun_sensor_index == "-Y":
        return cubesat.sun_yn.lux
    elif sun_sensor_index == "-Z":
        return cubesat.sun_zn.lux
    elif sun_sensor_index == "-X":
        return cubesat.sun_xn.lux
    elif sun_sensor_index == "+Y":
        return cubesat.sun_yp.lux
    elif sun_sensor_index == "+Z":
        return cubesat.sun_zp.lux
    elif sun_sensor_index == "+X":
        return cubesat.sun_xp.lux
    else:
        raise ValueError(f"Sun sensor index {sun_sensor_index} is not defined.")


def user_test(sensor_index, light_dark):
    """
    Ask the user to type y/any key to start/cancel the test
    If y, collect lux data for the given sensor
    If any other key, return  None
    """

    # start test, print user prompts based on light_dark
    print(f"Testing Sun Sensor {sensor_index} in the {light_dark}.")
    if light_dark == "Light":
        print("Please turn on the lights.")
    elif light_dark == "Dark":
        print("Please remove all nearby light sources or cover the sensor.")

    # ask user input to start test. if user cancels, return None
    start_test = input("Type Y to start the test, any key to cancel: ")
    if start_test.lower() != "y":
        return None

    # else continue
    print("Collecting sensor data...")
    lux_val = lux(sensor_index)
    print("Data collection complete.")
    return lux_val


def test_individual_sun_sensor(result_dict, sensor_index, light_dark):
    """
    Get result of user_test
    If result is None, update the result dictionary that the test was not run
    Else, check that lux reading is within a certain range and update the
    result dictionary
    """

    # get lux value from the user test
    lux_val = user_test(sensor_index, light_dark)

    # find result key and result value strings
    result_key = f"Sun{sensor_index}_{light_dark}"

    # if lux value is None, test was cancelled, update result dict and continue
    if lux_val is None:
        result_dict[result_key] = (
            f"Could not get a lux value for Sun Sensor {sensor_index}. Test cancelled or failed.", False)
        return result_dict

    # else continue
    result_val_string = (f"""Testing Sun Sensor {sensor_index} in the {light_dark} resulted
    in a lux value of {lux_val}""")

    if light_dark == "Light":
        # 100 is enough to illuminate small room
        result_val_bool = lux_val is not None and lux_val >= 100
        result_dict[result_key] = (result_val_string, result_val_bool)

    elif light_dark == "Dark":
        # 50 is about equal to low indoor light
        result_val_bool = lux_val is not None and lux_val < 50
        result_dict[result_key] = (result_val_string, result_val_bool)

    return result_dict


async def run(result_dict):
    """
    Check Sun Sensor -Y, -Z, -X, +Y, +Z, +X
    If initialized correctly, run test and update result dictionary through
    test_individual_sun_sensor
    If not initialized, update result dictionary
    """

    # if no Sun Sensor -Y detected, update result dictionary
    if not cubesat.sun_yn:
        result_dict["Sun-Y_Light"] = ("No sun sensor -Y detected", None)
        result_dict["Sun-Y_Dark"] = ("No sun sensor -Y detected", None)
    else:  # Sun Sensor -Y detected, run tests
        print("Starting Sun Sensor -Y test...")
        test_individual_sun_sensor(result_dict, "-Y", "Light")
        test_individual_sun_sensor(result_dict, "-Y", "Dark")
        print("Sun Sensor -Y test complete.\n")

    # if no Sun Sensor -Z detected, update result dictionary
    if not cubesat.sun_zn:
        result_dict["Sun-Z_Light"] = ("No sun sensor -Z detected", None)
        result_dict["Sun-Z_Dark"] = ("No sun sensor -Z detected", None)
    else:  # Sun Sensor -Z detected, run tests
        print("Starting Sun Sensor -Z test...")
        test_individual_sun_sensor(result_dict, "-Z", "Light")
        test_individual_sun_sensor(result_dict, "-Z", "Dark")
        print("Sun Sensor -Z test complete.\n")

    # if no Sun Sensor -X detected, update result dictionary
    if not cubesat.sun_xn:
        result_dict["Sun-X_Light"] = ("No sun sensor -X detected", None)
        result_dict["Sun-X_Dark"] = ("No sun sensor -X detected", None)
    else:  # Sun Sensor -X detected, run tests
        print("Starting Sun Sensor -X test...")
        test_individual_sun_sensor(result_dict, "-X", "Light")
        test_individual_sun_sensor(result_dict, "-X", "Dark")
        print("Sun Sensor -X test complete.\n")

    # if no Sun Sensor +Y detected, update result dictionary
    if not cubesat.sun_yp:
        result_dict["Sun+Y_Light"] = ("No sun sensor +Y detected", None)
        result_dict["Sun+Y_Dark"] = ("No sun sensor +Y detected", None)
    else:  # Sun Sensor +Y detected, run tests
        print("Starting Sun Sensor +Y test...")
        test_individual_sun_sensor(result_dict, "+Y", "Light")
        test_individual_sun_sensor(result_dict, "+Y", "Dark")
        print("Sun Sensor +Y test complete.\n")

    # if no Sun Sensor +Z detected, update result dictionary
    if not cubesat.sun_zp:
        result_dict["Sun+Z_Light"] = ("No sun sensor +Z detected", None)
        result_dict["Sun+Z_Dark"] = ("No sun sensor +Z detected", None)
    else:  # Sun Sensor +Z detected, run tests
        print("Starting Sun Sensor +Z test...")
        test_individual_sun_sensor(result_dict, "+Z", "Light")
        test_individual_sun_sensor(result_dict, "+Z", "Dark")
        print("Sun Sensor +Z test complete.\n")

    # if no Sun Sensor +X detected, update result dictionary
    if not cubesat.sun_xp:
        result_dict["Sun+X_Light"] = ("No sun sensor +X detected", None)
        result_dict["Sun+X_Dark"] = ("No sun sensor +X detected", None)
    else:  # Sun Sensor +X detected, run tests
        print("Starting Sun Sensor +X test...")
        test_individual_sun_sensor(result_dict, "+X", "Light")
        test_individual_sun_sensor(result_dict, "+X", "Dark")
        print("Sun Sensor +X test complete.\n")

    return result_dict
