try:
    from ulab.numpy import array
except Exception:
    from numpy import array

def hat(v):
    """Converts v to a matrix such that hat(v)w = cross(w, v) = -cross(v, w)"""
    return array([
        [0, -v[2], v[1]],
        [v[2], 0, -v[0]],
        [-v[1], v[0], 0]]
    )

def L(q):
    """Converts a quatenion to a left side matrix representing the given quaternion"""
    # qₛ, qᵥ = q[1], q[2:4]

    # M = [qₛ -qᵥ'
    # qᵥ qₛ*I(3)+hat(qᵥ)]

    return array([[1, 2, 3], [4, 5, 6]])
