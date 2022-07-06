import time
import math

def user_test(cubesat, result_dict, testidx):
    """
    fix tuple operations
    """

    wait_time = 30
    mag_time = 15

    if testidx == "Still":
        print("Please leave the cubesat flat on a table. Waiting", wait_time, "seconds.")
        time.sleep(wait_time)
        print("Collecting IMU data...")
        acc = cubesat.acceleration()
        gyro = cubesat.gyro()
        return acc, gyro, 0.0

    elif testidx == "Moving":
        print("Starting the moving test in", wait_time, "seconds.")
        time.sleep(wait_time)
        print("Please move the cubesat around for the next", wait_time, "seconds, starting now.")
        print("Collecting IMU data...")

        random_wait_time = math.random(1, wait_time)
        time.sleep(random_wait_time)
        mid_acc = cubesat.acceleration()
        gyro = cubesat.gyro()
        time.sleep(wait_time - random_wait_time)
        acc = mid_acc
        return acc, gyro, 0.0

    elif testidx == "Rotating":
        print("Please put cubesat on turntable. Waiting", wait_time, "seconds.")
        time.sleep(wait_time)
        print("Collecting IMU data...")
        acc = cubesat.acceleration()
        gyro = cubesat.gyro()
        return acc, gyro, 0.0

    elif testidx == "Magnet":
        print("Please leave the cubesat flat on a table and retrieve a magnet. \
            Waiting", wait_time, "seconds")
        time.sleep(wait_time)
        print("Please slowly move the magnet closer to the cubesat for", mag_time, "seconds")
        acc = cubesat.acceleration()
        gyro = cubesat.gyro()
        starting_mag = cubesat.magnetic()
        time.sleep(mag_time)
        ending_mag = cubesat.magnetic()

        mag = (math.sqrt(ending_mag[0] ** 2 + ending_mag[1] ** 2 + ending_mag[2] ** 2) -
               math.sqrt(starting_mag[0] ** 2 + starting_mag[1] ** 2 + starting_mag[2] ** 2))
        return acc, gyro, mag


def imu_test(cubesat, result_dict, testidx):
    if testidx == "Still":
        acc, gyro, mag = user_test(cubesat, result_dict, testidx)
        result_val_string = "Testing IMU when cubesat is still. Acc: " + str(acc) + ", \
            Gyro: " + str(gyro)

        if abs(acc[0]) < 0.2 and abs(acc[1]) < 0.2 and abs(9.8 - acc[2]) < 0.2:
            result_dict['IMU_Acc_Still'] = (result_val_string, True)
        else:
            result_dict['IMU_Acc_Still'] = (result_val_string, False)

        if abs(gyro[0]) < 0.2 and abs(gyro[1]) < 0.2 and abs(gyro[2]) < 0.2:
            result_dict['IMU_Gyro_Still'] = (result_val_string, True)
        else:
            result_dict['IMU_Gyro_Still'] = (result_val_string, False)

    elif testidx == "Moving":
        acc, gyro, mag = user_test(cubesat, result_dict, testidx)
        result_val_string = "Testing IMU when cubesat is being moved. Acc:\
             " + str(acc) + ", Gyro: " + str(gyro)
        if abs(acc[0]) > 0 and abs(acc[1]) > 0 and abs(acc[2]) > 0:
            result_dict['IMU_Acc_Moving'] = (result_val_string, True)
        else:
            result_dict['IMU_Acc_Moving'] = (result_val_string, False)

    elif testidx == "Rotating":
        acc, gyro, mag = user_test(cubesat, result_dict, testidx)
        result_val_string = "Testing IMU when cubesat is rotating on a turntable. Acc:\
             " + str(acc) + ", Gyro: " + str(gyro)

        ang_vel = input("Please enter the speed the turntable was rotating at: ")
        if abs(ang_vel - math.sqrt(gyro[0] ** 2 + gyro[1] ** 2 + gyro[2] ** 2)) < 0.2:
            result_dict['IMU_Gyro_Turntable'] = (result_val_string, True)
        else:
            result_dict['IMU_Gyro_Turntable'] = (result_val_string, False)

    elif testidx == "Magnet":
        acc, gyro, mag = user_test(cubesat, result_dict, testidx)
        result_val_string = "Testing IMU when cubesat is being moved. Acc:\
             " + str(acc) + ", Gyro: " + str(gyro) + ", Mag: " + str(mag)

        if mag > 0:
            result_dict['IMU_Gyro_Turntable'] = (result_val_string, True)
        else:
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
