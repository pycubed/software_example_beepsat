try:
    from ulab.numpy import array, vstack
except Exception:
    from numpy import array, vstack

def hat(v):
    """Converts v to a matrix such that hat(v)w = cross(w, v) = -cross(v, w)"""
    return array([
        [0, -v[2], v[1]],
        [v[2], 0, -v[0]],
        [-v[1], v[0], 0]]
    )

def L(q):
    """Converts a scalar-first unit quaternion into the left-side matrix for quaternion multiplication"""
    qs, qv = q[0], array([q[1:3]]).transpose()

    M = vstack()
    # M = [qₛ -qᵥ'
    # qᵥ qₛ*I(3)+hat(qᵥ)]

    return array([[1, 2, 3], [4, 5, 6]])
