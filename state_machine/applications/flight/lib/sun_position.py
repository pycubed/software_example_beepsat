# Based on: https://github.com/spacecraft-design-lab-2019/flight-software/blob/master/sun-position/sun_position.py
import math

def unix_time_to_julian_day(unix_time):
    """Takes in a unix timestamp and returns the julian day"""
    return unix_time / 86400 + 2440587.5

def approx_sun_position_ECI(utime):
    """
    Formula taken from "Satellite Orbits: Models, Methods and Applications" by Motenbruck and Gill
    See section 3.3.2 on page 70 for the formula
    Modified to take unix time as input.

    Args:
        - utime: unix timestamp

    Returns:
        - sun pointing in Earth Centered Intertial (ECI) frame
    """
    JD = unix_time_to_julian_day(utime)
    OplusW = 282.94  # Ω + ω
    T = (JD - 2451545.0) / 36525

    M = math.radians(357.5256 + 35999.049 * T)

    long = math.radians(OplusW + math.degrees(M) + 6892 / 3600 * math.sin(M) + 72 / 3600 * math.sin(2 * M))
    r_mag = (149.619 - 2.499 * math.cos(M) - 0.021 * math.cos(2 * M)) * 10**6

    epsilon = math.radians(23.43929111)
    r_vec = (r_mag * math.cos(long),
             r_mag * math.sin(long) * math.cos(epsilon),
             r_mag * math.sin(long) * math.sin(epsilon))

    return r_vec
