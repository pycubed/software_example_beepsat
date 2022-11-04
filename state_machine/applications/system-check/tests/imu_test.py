"""
Python system check script for PyCubed satellite board
PyCubed Mini mainboard-v02 for Pocketqube Mission
IMU Sensor Test
* Author(s): Yashika Batra
"""

import time
from ulab import numpy
from lib.pycubed import cubesat
from print_utils import bold, normal
import tasko


wait_time = 3
norm = numpy.linalg.norm
ACCEL_THRESHOLD = 1.5


def request_imu_data(prompt):
    """
    Prompt the user to start/cancel IMU readings
    Return IMU readings
    """

    print(prompt)
    start_test = input("Type Y to start the test, any key to cancel: ")
    if start_test.lower() != "y":
        return None

    time.sleep(0.5)
    print("Collecting IMU data...")

    # collect starting and ending mag readings
    # total acc and gyro readings; do 10 reads over 3 sec
    start_mag = numpy.array(cubesat.magnetic)
    acc_total = numpy.array([0., 0., 0.])
    gyro_total = numpy.array([0., 0., 0.])
    for _ in range(10):
        acc_total += numpy.array(cubesat.acceleration)
        gyro_total += numpy.array(cubesat.gyro)
        time.sleep(0.3)
    end_mag = numpy.array(cubesat.magnetic)

    acc_average = acc_total / 10
    gyro_average = gyro_total / 10
    mag_change = norm(end_mag - start_mag)

    print("Data Collection Complete")
    return acc_average, gyro_average, mag_change


def expect_gyro(operator, expected, op_desc):
    """
    Returns if operator(gyro reading, expected) is true
    """
    reading = cubesat.gyro
    if operator(reading, expected):
        return (f"{tuple(reading)} is {op_desc} {expected}", True)
    else:
        return (f"{tuple(reading)} is not {op_desc} {expected}", False)

def expect_acceleration(axis, expected):
    """
    Check that with +axis board facing up we get roughly the expected vector
    """
    input(f"Place the cubesat with the {bold}+{axis}{normal} board facing up and press enter: ")
    acc = cubesat.acceleration
    err = norm(acc - expected)
    if err > ACCEL_THRESHOLD:
        return (f"Read {tuple(acc)} instead of {tuple(expected)} for +{axis} board facing up," +
                f"error {err}>{ACCEL_THRESHOLD}", False)
    else:
        return (f"error {err}<={ACCEL_THRESHOLD}", True)


def magnet_imu_test(result_dict):
    """
    Check that the magnetometer reading increased as the magnet was
    moved closer
    """
    prompt = f"""Please slowly move the magnet closer to the cubesat for
{wait_time} seconds once you start the test."""
    res = request_imu_data(prompt)

    if res is None:
        result_dict["IMU_MagMagnet"] = ("Magnet test not completed.", None)
        return

    _, _, mag = res
    mag_string = (f"Change in Mag Reading: {mag} (µT)")
    mag_increasing = mag >= 10

    if mag_increasing:
        print(f"Increase of magnetometer reading ({mag} µT) ≥ 10 µT")
    else:
        print(f"Increase of magnetometer reading ({mag} µT) < 10 µT")

    result_dict["IMU_MagMagnet"] = (mag_string, mag_increasing)


def temp_imu_test(result_dict):
    """
    Verify that the temperature sensor on the IMU returns a reasonable
    value
    """
    temp = cubesat.temperature_imu
    print(f"IMU Temperature Reading: {temp} °C.")
    temp_in_range = 20 <= temp <= 80

    result_dict["IMU_Temp"] = (f"Temperature: {temp} °C", temp_in_range)

def update_result_dict_from_list(result_dict, result_list, all_passed_key, all_passed_str):
    """
    If all tests passed, update result dictionary with all_passed_key and all_passed_str
    Otherwise update result dictionary with all tests in result_list
    """
    all_passed = True
    for (key, (msg, passed)) in result_list:
        if not passed:
            all_passed = False
            break
    if all_passed:
        result_dict[all_passed_key] = (all_passed_str, True)
    else:
        for (key, (msg, passed)) in result_list:
            result_dict[key] = (msg, passed)

async def run(result_dict):
    """
    If initialized correctly, run tests and update result dictionary
    If not initialized, update result dictionary.
    Tests include:
    - Check gyro reading is near 0 when stationary
    - Check accelerometer reads g correctly in all 3 directions
    - Check gyro reading is more than 1 when rotated
    - Check magnetometer readings increase as a magnet is moved closer
    - Check the temperature is within a reasonable range
    """

    if not cubesat.imu:
        result_dict["IMU"] = ("Not detected", False)
        return
    else:
        result_dict["IMU"] = ("Detected", True)

    # accelerometer tests
    dirs = [
        ("X", numpy.array([9.8, 0, 0])),
        ("Y", numpy.array([0, 9.8, 0])),
        ("Z", numpy.array([0, 0, 9.8])),
    ]
    accel_results = []
    for (axis, expected) in dirs:
        res = expect_acceleration(axis, expected)
        accel_results.append((f"IMU_Accel_{axis}", res))
    update_result_dict_from_list(result_dict, accel_results, "IMU_Accel", "Success")

    # gyro tests
    gyro_results = []
    input("Place the cubesat on a flat surface and press enter: ")
    gyro_results.append(
        ("IMU_Gyro_Stationary", expect_gyro(lambda x, y: norm(x) < y, 1, "less in magnitude than"))
    )
    input("Move the cubesat around for a few seconds after pressing enter: ")
    await tasko.sleep(1.0)
    gyro_results.append(
        ("IMU_Gyro_Moving", expect_gyro(lambda x, y: norm(x) > y, 1, "greater in magnitude than"))
    )
    update_result_dict_from_list(result_dict, gyro_results, "IMU_Gyro", "Success")

    # if IMU detected, run other tests
    # else:
    #     print("Starting IMU Stationary Test...")
    #     stationary_imu_test(result_dict)
    #     print("IMU Stationary Test complete.\n")

    #     print("Starting IMU Rotating Test...")
    #     rotating_imu_test(result_dict)
    #     print("IMU Rotating Test complete.\n")

    #     print("Starting IMU Magnet Test...")
    #     magnet_imu_test(result_dict)
    #     print("IMU Magnet Test complete.\n")

    #     print("Starting IMU Temperature Test...")
    #     temp_imu_test(result_dict)
    #     print("IMU Temperature Test complete.\n")

    # return result_dict
