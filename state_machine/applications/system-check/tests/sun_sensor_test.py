from lib.pycubed import cubesat
from print_utils import bold, normal

def test_sun_sensor(sensor, sensor_name, sensors):
    """
    Tests if a sun sensor is:
        - Detected
        - Driver sensor coresponds to the correct physical sensor
    """
    if sensor is None:
        return ("not detected", False)
    input(f'Place the {bold}{sensor_name}{normal} board face down on the table, then press enter: ')
    min_lux = sensor.lux
    for i in range(len(sensors)):
        (other, other_name) = sensors[i]
        if other is None:
            continue
        lux = other.lux
        if lux < min_lux and other != sensor:
            return (f"{sensor_name} should read the lowest lux, but {other_name} read lower ({min_lux} > {lux})", False)
    return ("success", True)


async def run(result_dict):
    """
    Check all that all sun sensors exists, and are properly configured
    """
    print("Testing Sun Sensors\n")
    sensors = [
        (cubesat.sun_xn, "X-"),
        (cubesat.sun_xp, "X+"),
        (cubesat.sun_yn, "Y-"),
        (cubesat.sun_yp, "Y+"),
        (cubesat.sun_zn, "Z-"),
        (cubesat.sun_zp, "Z+"),
    ]
    for (sensor, sensor_name) in sensors:
        (str, success) = test_sun_sensor(sensor, sensor_name, sensors)
        result_dict[f'Sun Sensor {sensor_name}'] = (str, success)
        if not success:
            print(f'Sun Sensor {sensor_name} failed: {str}')

    print("Done Testing Sun Sensors\n")
