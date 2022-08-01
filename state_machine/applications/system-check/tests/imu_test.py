"""
Python system check script for PyCubed satellite board
PyCubed Mini mainboard-v02 for Pocketqube Mission
IMU Sensor Test
* Author(s): Yashika Batra
"""

import time
from ulab.numpy.linalg import norm
import random
from lib import pycubed as cubesat


wait_time = 3


def still_user_test():
    """
    All user interaction for the still test happens in this function
    Set wait times, prompt the users and gather IMU data and input
    """
    # print user prompts
    print(("Please leave the cubesat flat on a table." +
           "Waiting {} seconds.").format(wait_time))
    time.sleep(wait_time)
    print("Collecting IMU data...")

    # collect acceleration and gyroscope readings, return 0.0 mag default
    time.sleep(wait_time)
    acc = cubesat.acceleration()
    gyro = cubesat.gyro()
    print("Data Collection Complete")
    return acc, gyro, 0.0


def still_imu_test(result_dict):
    """
    All still test automation happens in this function
    Process user test results and update the result dictionary accordingly
    """
    # record acceleration
    acc, gyro, mag = still_user_test()
    result_val_string_acc = ("Testing IMU when cubesat is still." +
                             "Acc: {}").format(acc)
    result_val_string_gyro = ("Testing IMU when cubesat is still." +
                              "Gyro: {}").format(gyro)

    # if total acceleration ~= 9.8 m/s^2 and gyro ~= 0 deg/s, true
    result_val_bool_acc = 9.8 - norm(acc) < 0.2
    result_val_bool_gyro = norm(gyro) < 0.2
    result_dict['IMU_AccStill'] = (
        result_val_string_acc, result_val_bool_acc)
    result_dict['IMU_GyroStill'] = (
        result_val_string_gyro, result_val_bool_gyro)


def moving_user_test():
    """
    All user interaction for the moving test happens in this function
    Set wait times, prompt the users and gather IMU data and input
    """
    # print user prompts
    print("Starting the moving test in {} seconds.".format(wait_time))
    time.sleep(wait_time)
    print(("Please move the cubesat around for the next {} " +
           "seconds, starting now.").format(wait_time))
    print("Collecting IMU data...")

    # at some random time, collect acc and gyro readings, return 0.0 mag
    random_wait_time = random.randint(1, wait_time)
    time.sleep(random_wait_time)
    acc = cubesat.acceleration()
    gyro = cubesat.gyro()
    time.sleep(wait_time - random_wait_time)
    print("Data Collection Complete")
    return acc, gyro, 0.0


def moving_imu_test(result_dict):
    """
    All moving test automation happens in this function
    Process user test results and update the result dictionary accordingly
    """
    # record acceleration
    acc, gyro, mag = moving_user_test()
    result_val_string = ("Testing IMU when cubesat is being moved." +
                         "Acc: {}").format(acc)

    # if absolute value of each acceleration component is more than 0, true
    result_val_bool = norm(acc) >= 0.1
    result_dict['IMU_AccMoving'] = (result_val_string, result_val_bool)


def rotating_user_test():
    """
    All user interaction for the rotating test happens in this function
    Set wait times, prompt the users and gather IMU data and input
    """
    # print user prompts
    print(("Please rotate the cubesat as best as possible." +
           "Waiting {} seconds.").format(wait_time))
    time.sleep(wait_time)
    print("Collecting IMU data...")

    # at some random time, collect acc and gyro readings, return 0.0 mag
    random_wait_time = random.randint(1, wait_time)
    time.sleep(random_wait_time)
    acc = cubesat.acceleration()
    gyro = cubesat.gyro()
    time.sleep(wait_time - random_wait_time)
    print("Data Collection Complete")
    return acc, gyro, 0.0


def rotating_imu_test(result_dict):
    """
    All rotating test automation happens in this function
    Process user test results and update the result dictionary accordingly
    """
    # record gyro reading
    acc, gyro, mag = rotating_user_test()
    result_val_string = ("Testing IMU when cubesat is rotating." +
                         "Gyro: {}").format(gyro)

    # if total gyro reading when rotating is greater than 0, true
    result_val_bool = norm(gyro) >= 0.2
    result_dict['IMU_GyroRotating'] = (result_val_string, result_val_bool)


def magnet_user_test():
    """
    All user interaction for the magnet test happens in this function
    Set wait times, prompt the users and gather IMU data and input
    """
    # print user prompts
    print(("Please leave the cubesat flat on a table and retrieve a " +
           "magnet. Waiting {} seconds.").format(wait_time))
    time.sleep(wait_time)
    print(("Please slowly move the magnet closer to the cubesat " +
           "for {} seconds.").format(wait_time))
    print("Collecting IMU data...")

    # collect acc, gyro, mag at the start, and mag at end
    acc = cubesat.acceleration()
    gyro = cubesat.gyro()
    starting_mag = cubesat.magnetic()
    time.sleep(wait_time)
    ending_mag = cubesat.magnetic()
    # calculate the change in the total magnetometer reading
    mag = norm(starting_mag - ending_mag)
    print("Data Collection Complete")
    return acc, gyro, mag


def magnet_imu_test(result_dict):
    """
    All magnet test automation happens in this function
    Process user test results and update the result dictionary accordingly
    """
    # record magnetometer reading
    acc, gyro, mag = magnet_user_test()
    result_val_string = (
        ("Testing IMU when cubesat is subject to an external magnetic" +
         "field. Change in Mag Reading: {}").format(mag))

    # if change in magnetometer reading is more than 0, true
    result_val_bool = mag >= 0.2
    result_dict['IMU_MagMagnet'] = (result_val_string, result_val_bool)


def temp_imu_test(result_dict):
    """
    All temperature test functions happen in this function
    Update the result dictionary accordingly
    """
    # collect temperature reading, ask user to confirm
    temp = cubesat.temperature_imu()
    print("IMU Temperature Reading: {}".format(temp))
    print(("Generally, room temperature is between {} and {}" +
           "degrees celsius.").format(20, 27))
    res = input("Does the temperature reading look correct? (Y/N): ")
    result_val_bool = False
    if res == "Y":
        result_val_bool = True
    result_dict['IMU_Temp'] = ("IMU Temperature Reading: {}".format(temp),
                               result_val_bool)


def run(hardware_dict, result_dict):
    """
    Check that the correct hardware is initialized and run tests
    """

    # if no IMU detected, update result dictionary and return
    if not hardware_dict['IMU']:
        result_dict['IMU_AccStill'] = (
            'Cannot test accelerometer; no IMU detected', False)
        result_dict['IMU_AccMoving'] = (
            'Cannot test accelerometer; no IMU detected', False)
        result_dict['IMU_GyroStill'] = (
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
        still_imu_test(result_dict)
        moving_imu_test(result_dict)
        rotating_imu_test(result_dict)
        magnet_imu_test(result_dict)
        temp_imu_test(result_dict)
        print("IMU Test complete.")
        print("")

    return result_dict
