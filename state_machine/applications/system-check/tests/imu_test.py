"""
Python system check script for PyCubed satellite board
PyCubed Mini mainboard-v02 for Pocketqube Mission
IMU Sensor Test
* Author(s): Yashika Batra
"""

import time
from math import sqrt
import random
from lib import pycubed as cubesat


def user_test(test_type):
    """
    All user interaction happens in this function
    Set wait times, prompt the users and gather IMU data and input
    """

    wait_time = 3

    if test_type == "Still":
        # print user prompts
        print("Please leave the cubesat flat on a table. Waiting",
              wait_time, "seconds.")
        time.sleep(wait_time)
        print("Collecting IMU data...")

        # collect acceleration and gyroscope readings, return 0.0 mag default
        time.sleep(wait_time)
        acc = cubesat.acceleration()
        gyro = cubesat.gyro()
        print("Data Collection Complete")
        return acc, gyro, 0.0

    elif test_type == "Moving":
        # print user prompts
        print("Starting the moving test in", wait_time, "seconds.")
        time.sleep(wait_time)
        print("Please move the cubesat around for the next", wait_time,
              "seconds, starting now.")
        print("Collecting IMU data...")

        # at some random time, collect acc and gyro readings, return 0.0 mag
        random_wait_time = random.randint(1, wait_time)
        time.sleep(random_wait_time)
        acc = cubesat.acceleration()
        gyro = cubesat.gyro()
        time.sleep(wait_time - random_wait_time)
        print("Data Collection Complete")
        return acc, gyro, 0.0

    elif test_type == "Rotating":
        # print user prompts
        print("Please rotate the cubesat as best as possible. Waiting",
              wait_time, "seconds.")
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

    elif test_type == "Magnet":
        # print user prompts
        print("Please leave the cubesat flat on a table and retrieve a " +
              "magnet. " + "Waiting", wait_time, "seconds")
        time.sleep(wait_time)
        print("Please slowly move the magnet closer to the cubesat for",
              wait_time, "seconds")
        print("Collecting IMU data...")

        # collect acc, gyro, mag at the start, and mag at end
        acc = cubesat.acceleration()
        gyro = cubesat.gyro()
        starting_mag = cubesat.magnetic()
        time.sleep(wait_time)
        ending_mag = cubesat.magnetic()
        # calculate the change in the total magnetometer reading
        mag = (sqrt(ending_mag[0] ** 2 + ending_mag[1] ** 2 +
               ending_mag[2] ** 2) - sqrt(starting_mag[0] ** 2 +
               starting_mag[1] ** 2 + starting_mag[2] ** 2))
        print("Data Collection Complete")
        return acc, gyro, mag


def imu_test(result_dict, test_type):
    """
    All automation happens in this function
    Process user test results and update the result dictionary accordingly
    """
    if test_type == "Still":
        # record acceleration
        acc, gyro, mag = user_test(test_type)
        result_val_string_acc = ("Testing IMU when cubesat is still. Acc: " +
                                 str(acc))
        result_val_string_gyro = ("Testing IMU when cubesat is still. Gyro: " +
                                  str(gyro))

        # if total acceleration ~= 9.8 m/s^2 and gyro ~= 0 deg/s, true
        result_val_bool_acc = abs(
            9.8 - sqrt(acc[0] ** 2 + acc[1] ** 2 + acc[2] ** 2)) < 0.2
        result_val_bool_gyro = sqrt(
            gyro[0] ** 2 + gyro[1] ** 2 + gyro[2] ** 2) < 0.2
        result_dict['IMU_AccStill'] = (
            result_val_string_acc, result_val_bool_acc)
        result_dict['IMU_GyroStill'] = (
            result_val_string_gyro, result_val_bool_gyro)

    elif test_type == "Moving":
        # record acceleration
        acc, gyro, mag = user_test(test_type)
        result_val_string = ("Testing IMU when cubesat is being moved. Acc: " +
                             str(acc))

        # if absolute value of each acceleration component is more than 0, true
        result_val_bool = (abs(acc[0]) > 0 and abs(acc[1]) > 0 and
                           abs(acc[2]) > 0)
        result_dict['IMU_AccMoving'] = (result_val_string, result_val_bool)

    elif test_type == "Rotating":
        # record gyro reading
        acc, gyro, mag = user_test(test_type)
        result_val_string = ("Testing IMU when cubesat is rotating. Gyro: " +
                             str(gyro))

        # if total gyro reading when rotating is greater than 0, true
        total_gyro = sqrt(gyro[0] ** 2 + gyro[1] ** 2 + gyro[2] ** 2)
        result_val_bool = total_gyro > 0

        result_dict['IMU_GyroRotating'] = (result_val_string, result_val_bool)

    elif test_type == "Magnet":
        # record magnetometer reading
        acc, gyro, mag = user_test(test_type)
        result_val_string = (
            "Testing IMU when cubesat is subject to an external magnetic" +
            "field. Change in Mag Reading: " + str(mag))

        # if change in magnetometer reading is more than 0, true
        result_val_bool = mag > 0
        result_dict['IMU_MagMagnet'] = (result_val_string, result_val_bool)

    elif test_type == "Temp":
        # collect temperature reading, ask user to confirm
        temp = cubesat.temperature_imu()
        print("IMU Temperature Reading: " + str(temp))
        res = input("Does the temperature reading look correct? (Y/N): ")
        result_val_bool = False
        if res == "Y":
            result_val_bool = True
        result_dict['IMU_Temp'] = ("IMU Temperature Reading: " + str(temp),
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
        imu_test(result_dict, "Still")
        imu_test(result_dict, "Moving")
        imu_test(result_dict, "Rotating")
        imu_test(result_dict, "Magnet")
        imu_test(result_dict, "Temp")
        print("IMU Test complete.")
        print("")

    return result_dict
