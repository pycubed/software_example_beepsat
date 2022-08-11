"""
Python system check script for PyCubed satellite board
PyCubed Mini mainboard-v02 for Pocketqube Mission
IMU Sensor Test
* Author(s): Yashika Batra
"""

import time
from ulab import numpy
from lib import pycubed as cubesat


wait_time = 3
norm = numpy.linalg.norm


def request_imu_data(prompt):
    """
    Print the given prompt and ask the user the start/cancel the test
    Collect IMU readings and return
    """

    print(prompt)
    start_test = input("Type Y to start the test, any key to cancel: ")
    if start_test.lower() != "y":
        return None

    time.sleep(0.5)
    print("Collecting IMU data...")

    # collect starting and ending mag readings
    # total acc and gyro readings; do 10 reads over 3 sec
    start_mag = numpy.array(cubesat.magnetic())
    acc_total = numpy.array([0., 0., 0.])
    gyro_total = numpy.array([0., 0., 0.])
    for _ in range(10):
        acc_total += numpy.array(cubesat.acceleration())
        gyro_total += numpy.array(cubesat.gyro())
        time.sleep(0.3)
    end_mag = numpy.array(cubesat.magnetic())

    acc_average = acc_total / 10
    gyro_average = gyro_total / 10
    mag_change = norm(end_mag - start_mag)

    # return average acc, average gyro, change in mag
    print("Data Collection Complete")
    return acc_average, gyro_average, mag_change


def check_gravity_acc(acc1, acc2, acc3):
    # acc1 directions
    xdir1 = abs(norm(numpy.dot(acc1, [1, 0, 0])) - 9.8) < 1
    ydir1 = abs(norm(numpy.dot(acc1, [0, 1, 0])) - 9.8) < 1
    zdir1 = abs(norm(numpy.dot(acc1, [0, 0, 1])) - 9.8) < 1

    # acc2 directions
    xdir2 = abs(norm(numpy.dot(acc2, [1, 0, 0])) - 9.8) < 1
    ydir2 = abs(norm(numpy.dot(acc2, [0, 1, 0])) - 9.8) < 1
    zdir2 = abs(norm(numpy.dot(acc2, [0, 0, 1])) - 9.8) < 1

    # acc3 directions
    xdir3 = abs(norm(numpy.dot(acc3, [1, 0, 0])) - 9.8) < 1
    ydir3 = abs(norm(numpy.dot(acc3, [0, 1, 0])) - 9.8) < 1
    zdir3 = abs(norm(numpy.dot(acc3, [0, 0, 1])) - 9.8) < 1

    # put everything in an array and count # of true values
    accboolarr = [xdir1, ydir1, zdir1, xdir2, ydir2,
                  zdir2, xdir3, ydir3, zdir3]
    count = 0
    for accbool in accboolarr:
        if accbool:
            count += 1

    return count == 3


def gravity_imu_test(result_dict):
    # TODO: refactor this

    # get readings from all 3 sides
    prompt1 = "Please leave the cubesat flat on one side."
    res1 = request_imu_data(prompt1)
    if res1 is None:
        result_dict["IMU_AccGravity"] = (
            "Gravity test not completed.", None)
        return result_dict
    acc1, _, _ = res1

    prompt2 = "Please leave the cubesat flat on another side."
    res2 = request_imu_data(prompt2)
    if res2 is None:
        result_dict["IMU_AccGravity"] = (
            "Gravity test not completed.", None)
        return result_dict
    acc2, _, _ = res2

    prompt3 = "Please leave the cubesat flat on another side."
    res3 = request_imu_data(prompt3)
    if res3 is None:
        result_dict["IMU_AccGravity"] = (
            "Gravity test not completed.", None)
        return result_dict
    acc3, _, _ = res3

    result = check_gravity_acc(acc1, acc2, acc3)
    if result:
        result_string = "X, Y, and Z directions successful in reading g m/s^2."
        print(result_string)
        result_dict["IMU_AccGravity"] = (result_string, True)
    else:
        result_string = "Failed to read g m/s^2 in at least one direction."
        print(result_string)
        result_dict["IMU_AccGravity"] = (result_string, False)
    return result_dict


def stationary_imu_test(result_dict):
    """
    Check that norm of gyro is near 0
    """
    # prompt user and get imu data
    prompt = "Please leave the cubesat stationary on a table."
    res = request_imu_data(prompt)

    if res is None:
        result_dict["IMU_GyroStationary"] = (
            "Stationary test not completed.", None)
        return result_dict

    _, gyro, _ = res
    gyro_string = f"Gyro: {tuple(gyro)} (deg/s)"
    gyro_is_stationary = norm(gyro) < 1

    # print result to user
    if gyro_is_stationary:
        print("Stationary gyroscope reading is near 0 deg/s.")
    else:
        print("Stationary gyroscope reading is not near 0 deg/s.")

    # update result dictionary
    result_dict["IMU_GyroStationary"] = (gyro_string, gyro_is_stationary)
    return result_dict


def rotating_imu_test(result_dict):
    """
    Check that the norm of gyro is more than 0
    """
    # prompt user and get imu data
    prompt = f"""Please rotate the cubesat as best as possible for {wait_time}
seconds once you start the test."""
    res = request_imu_data(prompt)

    if res is None:
        # user entered "n", cancel the test
        result_dict["IMU_GyroRotating"] = (
            "Rotating test not completed.", None)
        return result_dict

    _, gyro, _ = res
    gyro_string = (f"Gyro: {tuple(gyro)} (deg/s)")
    gyro_is_rotating = norm(gyro) >= 1

    # print result to user
    if gyro_is_rotating:
        print("Rotating gyroscope reading is approx. greater than 0 deg/s.")
    else:
        print("Rotating gyroscope reading is near 0 deg/s.")

    # update result dictionary
    result_dict["IMU_GyroRotating"] = (gyro_string, gyro_is_rotating)
    return result_dict


def magnet_imu_test(result_dict):
    """
    Check that the magnetometer reading increased as the magnet was
    moved closer
    """
    # prompt user and get imu data
    prompt = f"""Please slowly move the magnet closer to the cubesat for
{wait_time} seconds once you start the test."""
    res = request_imu_data(prompt)

    if res is None:
        # user entered "n", cancel the test
        result_dict["IMU_MagMagnet"] = ("Magnet test not completed.", None)
        return result_dict

    _, _, mag = res
    mag_string = (f"Change in Mag Reading: {mag} (µT)")
    mag_is_increasing = mag >= 10

    # print result to user
    if mag_is_increasing:
        print("Magnetometer reading is increasing.")
    else:
        print("Magnetometer reading is not increasing.")

    # update result dictionary
    result_dict["IMU_MagMagnet"] = (mag_string, mag_is_increasing)
    return result_dict


def temp_imu_test(result_dict):
    """
    Verify that the temperature sensor on the IMU returns a reasonable
    value
    """
    # collect temperature reading, print to user
    temp = cubesat.temperature_imu()
    print(f"IMU Temperature Reading: {temp} degrees Celsius")
    result_val_bool = temp >= 20 and temp <= 80

    # update result dict based on user input
    result_dict["IMU_Temp"] = (f"Temperature: {temp}", result_val_bool)
    return result_dict


def run(hardware_dict, result_dict):
    """
    Check the IMU when the cubesat is stationary, moving, rotating,
    and around a magnetic field. Also check the IMU temperature sensor
    If initialized correctly, run test and update result dictionary
    If not initialized, update result dictionary
    """

    # if no IMU detected, update result dictionary and return
    if not hardware_dict["IMU"]:
        result_dict["IMU_AccGravity"] = (
            "Cannot test accelerometer; no IMU detected", None)
        result_dict["IMU_GyroStationary"] = (
            "Cannot test gyroscope; no IMU detected", None)
        result_dict["IMU_GyroRotating"] = (
            "Cannot test gyroscope; no IMU detected", None)
        result_dict["IMU_MagMagnet"] = (
            "Cannot test magnetometer; no IMU detected", None)
        result_dict["IMU_Temp"] = (
            "Cannot test temperature sensor; no IMU detected", None)
        return result_dict

    # if IMU detected, run other tests
    else:
        print("Starting IMU Stationary Test...")
        stationary_imu_test(result_dict)
        print("IMU Stationary Test complete.\n")

        print("Starting IMU Gravity Test...")
        gravity_imu_test(result_dict)
        print("IMU Gravity Test complete.\n")

        print("Starting IMU Rotating Test...")
        rotating_imu_test(result_dict)
        print("IMU Rotating Test complete.\n")

        print("Starting IMU Magnet Test...")
        magnet_imu_test(result_dict)
        print("IMU Magnet Test complete.\n")

        print("Starting IMU Temperature Test...")
        temp_imu_test(result_dict)
        print("IMU Temperature Test complete.\n")

    return result_dict
