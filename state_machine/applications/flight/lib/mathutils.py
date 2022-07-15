try:
    from ulab.numpy import array, ndarray, zeros, eye as I  # noqa: E741 (I is not ambiguous)
except Exception:
    from numpy import array, ndarray, zeros, eye as I  # noqa: E741 (I is not ambiguous)

def block(S):
    w = 0
    h = 0
    for m in S[0]:
        w += len(m[0])  # Take width of each element in first row
    for row in S:
        h += len(row[0])  # Take heigh of element in first column
    M = zeros((h, w))
    i = 0
    j = 0
    for row in S:
        di = len(row[0])
        for matrix in row:
            dj = len(matrix[0])
            M[i:i + di, j:j + dj] = matrix
            j += dj
        i += di
        j = 0
    return M


def hat(v):
    """Converts v to a matrix such that hat(v)w = cross(w, v) = -cross(v, w)"""
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

def Left(q):
    """Converts a scalar-first unit quaternion into the left-side matrix for quaternion multiplication"""
    if not isinstance(q, ndarray):
        q = array([q])
    if q.shape == (4,):
        qs, qv = q[0], array([q[1:4]]).transpose()
    elif q.shape == (4, 1):
        qs, qv = q[0], q[1:4]

    dr = qs * I(3) + hat(qv)
    M = block(
        [[array([[qs]]),  -qv.transpose()],
         [qv,            dr]])

    return M
