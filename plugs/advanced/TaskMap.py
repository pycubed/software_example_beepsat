from Tasks.battery_task import task as battery
from Tasks.beacon_task import task as beacon
from Tasks.blink_task import task as blink
from Tasks.imu_task import task as imu
from Tasks.time_task import task as time
from Tasks.test_task import task as test
from Tasks.lowpower5 import task as lowpower5
from Tasks.lowpower5later import task as lowpower5later

TaskMap = {
    "Battery": battery,
    "Beacon": beacon,
    "Blink": blink,
    "IMU": imu,
    "Time": time,
    "Test": test,
    "LowPower5": lowpower5,
    "LowPower5Later": lowpower5later,
}