try:
    import ulab.numpy as np
except ImportError:
    import numpy as np

def eci_to_ecef(date):
    """Returns the transformation matrix from ECI (Earth Centered Inertial) to ECEF (Earth Centered Earth Fixed).
    Applies corrections for bias, precession, nutation, Earth-rotation, and polar motion.

    The transformation is accomplished using the IAU 2006/2000A, CIO-based
    theory using classical angles. The method as described in section 5.5 of
    the SOFA C transformation cookbook.

    Args:
        - date: A unix timestamp.

    Returns:
        - A 3x3 numpy array.
    Based on: https://github.com/sisl/SatelliteDynamics.jl/blob/f1eede2faffd2d6a6864d7ac0989a075c7d7a04f/src/reference_systems.jl#L296
    """
    rc2i = bias_precession_nutation(date)
    r = earth_rotation(date)
    rpm = polar_motion(date)
    return np.dot(rc2i, np.dot(r, rpm))

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
