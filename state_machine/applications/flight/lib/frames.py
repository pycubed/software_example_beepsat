def eci_to_ecef(date):
    """Returns the transformation matrix from ECI (Earth Centered Inertial) to ECEF (Earth Centered Earth Fixed).
    Args:
        - date: A unix timestamp.

    Returns:
        - A 3x3 numpy array.
    """
    return None

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
