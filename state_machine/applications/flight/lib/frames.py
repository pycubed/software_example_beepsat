try:
    import ulab.numpy as np
    from ulab.numpy import cos, sin
except ImportError:
    import numpy as np
    from numpy import cos, sin

J2000 = 946684800  # unix timestamp for the Julian date 2000-01-01
MJD_ZERO = 2400000.5  # Offset of Modified Julian Days representation with respect to Julian Days.
JD2000 = 2451545.0  # Reference epoch (J2000.0), Julian Date
MJD2000 = 51544.5  # MJD at J2000.0
PI2 = 2 * np.pi

def mjd(utime):
    """Returns the Modified Julian Date (MJD) for a given unix timestamp."""
    return utime / 86400.0 + 40587

def rotZ(theta):
    return np.array([[cos(theta),   sin(theta), 0],
                     [-sin(theta),  cos(theta), 0],
                     [0,            0,          1]])

def ERA(utime):
    """Returns the the ERA (Earth Rotation Angle) at a certain unix time stamp.
    Inspired by SOFA's iauEra00 function.

    Args:
        - utime: A unix timestamp.

    Returned (function value):
        - ERA (Earth Rotation Angle) at this time stamp (radians)"""
    # Days since J2000.0.
    d = mjd(utime)
    days = d - MJD2000
    # Fractional part of T (days).
    f = (d % 1.0)
    # Earth rotation angle at this UT1.
    theta = (PI2 * (f + 1.2790572732640 + 0.00273781191135448 * days)) % (2 * PI2)

    return theta

def earth_rotation(utime):
    # Compute Earth rotation angle
    era = ERA(utime)
    # Rotate Matrix and return
    r = rotZ(era)
    return r

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
    # rc2i = bias_precession_nutation(epc)
    r    = earth_rotation(utime)
    # rpm  = polar_motion(epc)

    # return rpm @ r @ rc2i
    return r

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
