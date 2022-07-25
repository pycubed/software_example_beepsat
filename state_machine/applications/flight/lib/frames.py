try:
    import ulab.numpy as np
    from ulab.numpy import cos, sin
except ImportError:
    import numpy as np
    from numpy import cos, sin

J2000 = 946684800  # unix timestamp for the Julian date 2000-01-01
JYEAR = 31557600  # number of seconds in a Julian Year

def rotZ(theta):
    return np.array([[cos(theta),   sin(theta), 0],
                     [-sin(theta),  cos(theta), 0],
                     [0,            0,          1]])

def eci_to_ecef(utime):
    """Returns the transformation matrix from ECI (Earth Centered Inertial) to ECEF (Earth Centered Earth Fixed).
    Applies correction for Earth-rotation.
    Based on: https://space.stackexchange.com/a/53569

    Args:
        - date: A unix timestamp.

    Returns:
        - A 3x3 numpy array.
    Based on: https://github.com/sisl/SatelliteDynamics.jl/blob/f1eede2faffd2d6a6864d7ac0989a075c7d7a04f/src/reference_systems.jl#L296
    """
    # Julian centuries since J2000.0
    days = (utime - J2000) / 86164.0905  # days since J2000
    theta2020 = 4.89495042  # ERA (Earth Rotation Angle) at J2000.0
    perday = 6.300387487009043  # Radians rotated per day
    theta = days * perday + theta2020
    return rotZ(theta)

def ecef_to_eci(date):
    """Returns the transformation matrix from ECEF (Earth Centered Earth Fixed) to ECI (Earth Centered Inertial).
    Args:
        - date: A unix timestamp.

    Returns:
        - A 3x3 numpy array.
    """
    return eci_to_ecef(date).transpose()

def ned_to_ecef(lat, long):
    """ Returns the transformation matrix from NED (North East Down) to ECEF (Earth Centered Earth Fixed).
    Args:
        - lat: Latitude in radians (geocentric)
        - long: Longitude in radians (geocentric)

    Returns:
        - A 3x3 numpy array.
    """
    return None
