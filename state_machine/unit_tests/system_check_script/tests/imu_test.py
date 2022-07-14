"""
Python system check script for PyCubed satellite board
PyCubed Mini mainboard-v02 for Pocketqube Mission
IMU Sensor Test
* Author(s): Yashika Batra
"""

import time
from math import sqrt
import random
import pycubed

def user_test(cubesat, result_dict, testidx):
    """
    All user interaction happens in this function
    Set wait times, change print statement and input formatting, etc.
    """

    wait_time = 15
    mag_time = 15

    if testidx == "Still":
        print("Please leave the cubesat flat on a table. Waiting", wait_time, "seconds.")
        time.sleep(wait_time)
        print("Collecting IMU data...")

        acc = pycubed.acceleration
        gyro = pycubed.gyro
        print("Data Collection Complete")
        return acc, gyro, 0.0

    elif testidx == "Moving":
        print("Starting the moving test in", wait_time, "seconds.")
        time.sleep(wait_time)
        print("Please move the cubesat around for the next", wait_time, "seconds, starting now.")
        print("Collecting IMU data...")

        random_wait_time = random.randint(1, wait_time)
        time.sleep(random_wait_time)
        mid_acc = pycubed.acceleration
        gyro = pycubed.gyro
        time.sleep(wait_time - random_wait_time)
        acc = mid_acc
        print("Data Collection Complete")
        return acc, gyro, 0.0

    elif testidx == "Rotating":
        print("Please put cubesat on turntable. Waiting", wait_time, "seconds.")
        time.sleep(wait_time)
        print("Collecting IMU data...")

        acc = pycubed.acceleration
        gyro = pycubed.gyro
        print("Data Collection Complete")
        return acc, gyro, 0.0

    elif testidx == "Magnet":
        print("Please leave the cubesat flat on a table and retrieve a magnet. " +
              "Waiting", wait_time, "seconds")
        time.sleep(wait_time)
        print("Please slowly move the magnet closer to the cubesat for", mag_time, "seconds")

        acc = pycubed.acceleration
        gyro = pycubed.gyro
        starting_mag = pycubed.magnetic
        time.sleep(mag_time)
        ending_mag = pycubed.magnetic
        # calculate the change in the total magnetometer reading
        mag = (sqrt(ending_mag[0] ** 2 + ending_mag[1] ** 2 + ending_mag[2] ** 2) -
               sqrt(starting_mag[0] ** 2 + starting_mag[1] ** 2 + starting_mag[2] ** 2))
        print("Data Collection Complete")
        return acc, gyro, mag


def imu_test(cubesat, result_dict, testidx):
    """
    All automation happens in this function
    Select burnwire and voltage level
    Process user test results and update the result dictionary accordingly
    """
    if testidx == "Still":
        # record acceleration
        acc, gyro, mag = user_test(cubesat, result_dict, testidx)
        result_val_string = "Testing IMU when cubesat is still. Acc: " + str(acc)

        # if total acceleration is within 0.2 m/s^2 of 9.8, true
        if abs(9.8 - sqrt(acc[0] ** 2 + acc[1] ** 2 + acc[2] ** 2)) < 0.2:
            result_dict['IMU_Acc_Still'] = (result_val_string, True)
        else:  # else false
            result_dict['IMU_Acc_Still'] = (result_val_string, False)

    elif testidx == "Moving":
        # record acceleration
        acc, gyro, mag = user_test(cubesat, result_dict, testidx)
        result_val_string = "Testing IMU when cubesat is being moved. Acc: " + str(acc)

        # if each acceleration component is more than 0, true
        if abs(acc[0]) > 0 and abs(acc[1]) > 0 and abs(acc[2]) > 0:
            result_dict['IMU_Acc_Moving'] = (result_val_string, True)
        else:  # else false
            result_dict['IMU_Acc_Moving'] = (result_val_string, False)

    elif testidx == "Rotating":
        # record gyro reading
        acc, gyro, mag = user_test(cubesat, result_dict, testidx)
        result_val_string = "Testing IMU when cubesat is rotating on a turntable. Gyro: " + str(gyro)

        # if total gyro reading is within 2 deg/s^2 of angular velocity, return true
        ang_vel = float(input("Please enter the speed the turntable was rotating at in deg/s: "))
        if abs(ang_vel - sqrt(gyro[0] ** 2 + gyro[1] ** 2 + gyro[2] ** 2)) < 2:
            result_dict['IMU_Gyro_Turntable'] = (result_val_string, True)
        else:  # else false
            result_dict['IMU_Gyro_Turntable'] = (result_val_string, False)

    elif testidx == "Magnet":
        # record magnetometer reading
        acc, gyro, mag = user_test(cubesat, result_dict, testidx)
        result_val_string = ("Testing IMU when cubesat is subject to an external magnetic field." +
                             "Final Mag Reading: " + str(mag))

        # if change in magnetometer reading is more than 0, true
        if mag > 0:
            result_dict['IMU_Gyro_Turntable'] = (result_val_string, True)
        else:  # else false
            result_dict['IMU_Gyro_Turntable'] = (result_val_string, False)


def run(cubesat, hardware_dict, result_dict):
    # if no IMU detected, update result dictionary and return
    if not hardware_dict['IMU']:
        result_dict['IMU_Acc_Still'] = ('Cannot test accelerometer; no IMU detected', False)
        result_dict['IMU_Acc_Moving'] = ('Cannot test accelerometer; no IMU detected', False)
        result_dict['IMU_Gyro_Still'] = ('Cannot test gyroscope; no IMU detected', False)
        result_dict['IMU_Gyro_Turntable'] = ('Cannot test gyroscope; no IMU detected', False)
        result_dict['IMU_Mag_Standalone'] = ('Cannot test magnetometer; no IMU detected', False)
        result_dict['IMU_Mag_Magnet'] = ('Cannot test magnetometer; no IMU detected', False)
        result_dict['IMU_Temp'] = ('Cannot test temperature sensor; no IMU detected', False)
        return result_dict

    # if IMU detected, run other tests
    else:
        imu_test(cubesat, result_dict, "Still")
        imu_test(cubesat, result_dict, "Moving")
        imu_test(cubesat, result_dict, "Rotating")
        imu_test(cubesat, result_dict, "Magnet")

    return result_dict
