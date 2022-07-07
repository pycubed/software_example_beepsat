try:
    from ulab.numpy import array
except Exception:
    from numpy import array

def hat(v):
    """<<<>>>"""
    return array([
        [0, v[3], -v[2]],
        [-v[3], 0, v[1]],
        [v[2], -v[1], 0]]
    )
