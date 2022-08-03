"""
Python system check script for PyCubed satellite board
PyCubed Mini mainboard-v02 for Pocketqube Mission
IMU Sensor Test
* Author(s): Yashika Batra
"""

import time
from ulab import numpy
from lib import pycubed as cubesat


wait_time = 2
norm = numpy.linalg.norm


def stationary_user_test():
    """
    All user interaction for the stationary test happens in this function
    Set wait times, prompt the users and gather IMU data and input
    """
    # print user prompts
    print("Please leave the cubesat stationary on a table.")
    start_test = input("Type Y to start the stationary test, any key" +
                       " to cancel: ")

    # if user opts to cancel the test, return None, handle in the next function
    if start_test.lower() != "y":
        return None, None, None
    print("Collecting IMU data...")

    # collect acceleration and gyroscope readings, return None mag default
    time.sleep(wait_time)
    acc = cubesat.acceleration()
    gyro = cubesat.gyro()
    print("Data Collection Complete")
    return acc, gyro, None


def stationary_imu_test(result_dict):
    """
    All stationary test automation happens in this function
    Process user test results and update the result dictionary accordingly
    """
    # record acceleration
    acc, gyro, mag = stationary_user_test()
    if acc is None and gyro is None:
        # user entered "n", cancel the test
        result_dict['IMU_AccStationary'] = (
            "Stationary test not completed.", False)
        result_dict['IMU_GyroStationary'] = (
            "Stationary test not completed.", False)
        return result_dict

    # else continue running the test
    result_val_string_acc = f"Acc: {acc}"
    result_val_string_gyro = f"Gyro: {gyro}"

    # if total acceleration ~= 9.8 m/s^2 and gyro ~= 0 deg/s, true
    result_val_bool_acc = 9.8 - norm(acc) < 0.2
    result_val_bool_gyro = norm(gyro) < 0.2
    result_dict['IMU_AccStationary'] = (
        result_val_string_acc, result_val_bool_acc)
    result_dict['IMU_GyroStationary'] = (
        result_val_string_gyro, result_val_bool_gyro)
    return result_dict


def moving_user_test():
    """
    All user interaction for the moving test happens in this function
    Set wait times, prompt the users and gather IMU data and input
    """
    # print user prompts
    start_test = input("Type Y to start the moving test, any key to cancel: ")

    # if user opts to cancel the test, return None, handle in the next function
    if start_test.lower() != "y":
        return None, None, None

    # collect acc and gyro readings, return None mag
    print(f"Please move the cubesat around for the next {wait_time} " +
          "seconds, starting now.")
    print("Collecting IMU data...")
    time.sleep(wait_time // 2)
    acc = cubesat.acceleration()
    gyro = cubesat.gyro()
    time.sleep(wait_time - wait_time // 2)
    print("Data Collection Complete")
    return acc, gyro, None


def moving_imu_test(result_dict):
    """
    All moving test automation happens in this function
    Process user test results and update the result dictionary accordingly
    """
    # record acceleration
    acc, gyro, mag = moving_user_test()

    if acc is None:
        # user entered "n", cancel the test
        result_dict['IMU_AccMoving'] = ("Moving test not completed.", False)
        return result_dict

    # else continue running the test
    result_val_string = (f"Acc: {acc}")
    result_val_bool = norm(acc) >= 0.1
    result_dict['IMU_AccMoving'] = (result_val_string, result_val_bool)
    return result_dict


def rotating_user_test():
    """
    All user interaction for the rotating test happens in this function
    Set wait times, prompt the users and gather IMU data and input
    """
    # print user prompts
    start_test = input("Type Y to start the rotating test, any key" +
                       " to cancel: ")

    # if user opts to cancel the test, return None, handle in the next function
    if start_test.lower() != "y":
        return None, None, None

    # collect acc and gyro readings, return None mag
    print("Please rotate the cubesat as best as possible for " +
          f"{wait_time} seconds.")
    time.sleep(wait_time)
    print("Collecting IMU data...")
    time.sleep(wait_time // 2)
    acc = cubesat.acceleration()
    gyro = cubesat.gyro()
    time.sleep(wait_time - wait_time // 2)
    print("Data Collection Complete")
    return acc, gyro, None


def rotating_imu_test(result_dict):
    """
    All rotating test automation happens in this function
    Process user test results and update the result dictionary accordingly
    """
    # record gyro reading
    acc, gyro, mag = rotating_user_test()
    if gyro is None:
        # user entered "n", cancel the test
        result_dict["IMU_GyroRotating"] = (
            "Rotating test not completed.", False)
        return result_dict

    # else continue running the test
    result_val_string = (f"Gyro: {gyro}")
    result_val_bool = norm(gyro) >= 0.2
    result_dict['IMU_GyroRotating'] = (result_val_string, result_val_bool)
    return result_dict


def magnet_user_test():
    """
    All user interaction for the magnet test happens in this function
    Set wait times, prompt the users and gather IMU data and input
    """
    # print user prompts
    print("Please leave the cubesat flat on a table and retrieve a magnet.")
    start_test = input("Type Y to start the magnet test, any key to cancel: ")

    # if user opts to cancel the test, return None, handle in the next function
    if start_test.lower() != "y":
        return None, None, None

    # collect acc, gyro, mag at the start, and mag at end
    print("Please slowly move the magnet closer to the cubesat " +
          f"for {wait_time} seconds.")
    print("Collecting IMU data...")
    acc = cubesat.acceleration()
    gyro = cubesat.gyro()
    starting_mag = cubesat.magnetic()
    time.sleep(wait_time)
    ending_mag = cubesat.magnetic()

    # calculate the change in the total magnetometer reading
    sub_mag = tuple(map(
        lambda end, start: end - start, ending_mag, starting_mag))
    mag = norm(sub_mag)
    print("Data Collection Complete")
    return acc, gyro, mag


def magnet_imu_test(result_dict):
    """
    All magnet test automation happens in this function
    Process user test results and update the result dictionary accordingly
    """
    # record magnetometer reading
    acc, gyro, mag = magnet_user_test()
    if mag is None:
        # user entered "n", cancel the test
        result_dict["IMU_MagMagnet"] = ("Magnet test not completed.", False)
        return result_dict

    # else continue running the test
    result_val_string = (f"Change in Mag Reading: {mag}")
    result_val_bool = mag >= 0.2
    result_dict['IMU_MagMagnet'] = (result_val_string, result_val_bool)
    return result_dict


def temp_imu_test(result_dict):
    """
    All temperature test functions happen in this function
    Update the result dictionary accordingly
    """
    # collect temperature reading, ask user to confirm
    temp = cubesat.temperature_imu()
    print(f"IMU Temperature Reading: {temp}")
    print(f"Generally, room temperature is between {20} and {27}" +
          " degrees celsius.")

    # get user input on the correctness of the result
    res = input("Does the temperature reading look correct? (Y/N): ")
    result_val_bool = False
    if res.lower() == "y":
        result_val_bool = True

    # update result dict based on user input
    result_dict['IMU_Temp'] = (f"Temperature: {temp}", result_val_bool)
    return result_dict


def run(hardware_dict, result_dict):
    """
    Check that the correct hardware is initialized and run tests
    """

    # if no IMU detected, update result dictionary and return
    if not hardware_dict['IMU']:
        result_dict['IMU_AccStationary'] = (
            'Cannot test accelerometer; no IMU detected', False)
        result_dict['IMU_AccMoving'] = (
            'Cannot test accelerometer; no IMU detected', False)
        result_dict['IMU_GyroStationary'] = (
            'Cannot test gyroscope; no IMU detected', False)
        result_dict['IMU_GyroRotating'] = (
            'Cannot test gyroscope; no IMU detected', False)
        result_dict['IMU_MagMagnet'] = (
            'Cannot test magnetometer; no IMU detected', False)
        result_dict['IMU_Temp'] = (
            'Cannot test temperature sensor; no IMU detected', False)
        return result_dict

    # if IMU detected, run other tests
    else:
        print("Starting IMU test...")
        stationary_imu_test(result_dict)
        moving_imu_test(result_dict)
        rotating_imu_test(result_dict)
        magnet_imu_test(result_dict)
        temp_imu_test(result_dict)
        print("IMU Test complete.\n")

    return result_dict
