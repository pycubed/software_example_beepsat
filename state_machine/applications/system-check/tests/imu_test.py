import time
from ulab import numpy
from lib.pycubed import cubesat


wait_time = 3
norm = numpy.linalg.norm


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


def stationary_imu_test(result_dict):
    """
    Check that norm of gyro is less than 1 deg/s
    """
    prompt = "Please leave the cubesat stationary on a table."
    res = request_imu_data(prompt)

    if res is None:
        result_dict["IMU_GyroStationary"] = (
            "Stationary test not completed.", None)
        return

    _, gyro, _ = res
    gyro_string = f"Gyro: {tuple(gyro)} (deg/s)"
    gyro_stationary = norm(gyro) < 1

    if gyro_stationary:
        print(f"Stationary gyroscope reading has norm {norm(gyro)} < 1 deg/s.")
    else:
        print(f"Gyro reading is too large with norm {norm(gyro)} ≥ 1 deg/s.")

    result_dict["IMU_GyroStationary"] = (gyro_string, gyro_stationary)
    return


def check_gravity_acc(acc_readings):
    """
    Given 3 sets of acc readings, check that each set has one
    correct reading for g, in any order
    """

    # note if x, y, z readings are correct for each acc value
    # if there is a True value, find its index (x = 0, y = 1, z = 2)
    correct_directions = []
    for acc in acc_readings:
        correct_index = -1
        xdir = abs(abs(numpy.dot(acc, numpy.array([1, 0, 0]))) - 9.8) < 1
        ydir = abs(abs(numpy.dot(acc, numpy.array([0, 1, 0]))) - 9.8) < 1
        zdir = abs(abs(numpy.dot(acc, numpy.array([0, 0, 1]))) - 9.8) < 1
        if True in [xdir, ydir, zdir]:
            correct_index = [xdir, ydir, zdir].index(True)
        correct_directions.append(correct_index)

    # if a direction's index is in correct_directions, we read g correct in
    # that direction at least once. populate xyz_correct
    xyz_correct = [(i in correct_directions) for i in range(3)]
    result = xyz_correct == [True, True, True]
    return result, xyz_correct


def gravity_imu_test(result_dict):
    """
    Check that we read g correctly in all 3 directions, given any user
    input order
    """
    # get readings from all 3 sides
    acc_readings = []
    for i in range(3):
        prompt = "Please leave the cubesat flat on one side."
        if i > 0:
            prompt = "Please leave the cubesat flat on another side."
        res = request_imu_data(prompt)
        if res is None:
            result_dict["IMU_AccGravity"] = (
                "Gravity test not completed.", None)
            return
        acc, _, _ = res
        acc_readings.append(numpy.array(acc))

    result, xyz_correct = check_gravity_acc(acc_readings)
    xdir, ydir, zdir = xyz_correct

    if result:
        result_string = f"""Accelerometer read g as approx. 9.8 m/s^2 in
all 3 directions. x: {xdir}, y: {ydir}, z: {zdir}"""
    else:
        result_string = f"""Failed to read g m/s^2 in all 3 directions.
x: {xdir}, y: {ydir}, z: {zdir}"""

    print(result_string)
    result_dict["IMU_AccGravity"] = (result_string, result)


def rotating_imu_test(result_dict):
    """
    Check that the norm of gyro is greater than 1
    """
    prompt = f"""Please rotate the cubesat for {wait_time} seconds
once you start the test."""
    res = request_imu_data(prompt)

    if res is None:
        result_dict["IMU_GyroRotating"] = (
            "Rotating test not completed.", None)
        return

    _, gyro, _ = res
    gyro_string = (f"Gyro: {tuple(gyro)} (deg/s)")
    gyro_rotating = norm(gyro) >= 1

    if gyro_rotating:
        print(f"Gyro reading is correct with norm {norm(gyro)} ≥ 1 deg/s.")
    else:
        print(f"Gyro reading is too small with norm {norm(gyro)} < 1 deg/s.")

    result_dict["IMU_GyroRotating"] = (gyro_string, gyro_rotating)


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

    # if no IMU detected, update result dictionary and return
    if not cubesat.imu:
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
