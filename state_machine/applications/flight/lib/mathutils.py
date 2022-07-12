from numpy import identity


try:
    from ulab.numpy import array, block, ndarray
except Exception:
    from numpy import array, block, ndarray

def hat(v):
    """Converts v to a matrix such that hat(v)w = cross(w, v) = -cross(v, w)"""
    print(v)
    if not isinstance(v, ndarray):
        v = array(v)
    if v.shape == (3, 1):
        return array([
            [0,         -v[2][0],   v[1][0]],
            [v[2][0],    0,        -v[0][0]],
            [-v[1][0],   v[0][0],   0]])
    elif v.shape == (3,):
        return array([
            [0, -v[2], v[1]],
            [v[2], 0, -v[0]],
            [-v[1], v[0], 0]])
    else:
        raise ValueError("v must be a 3x1 numpy array")

def L(q):
    """Converts a scalar-first unit quaternion into the left-side matrix for quaternion multiplication"""
    qs, qv = q[0], array([q[1:4]]).transpose()
    print("qs: ", qs, "qv: ", qv)

    dr = qs * identity(3) + hat(qv)
    M = block([
        [qs,  -qv.transpose()],
        [qv,  dr]])

    return M
