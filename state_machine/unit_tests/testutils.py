from datetime import datetime as dt, timezone
import numpy as np

def timestamp(year, month, day, hour=0, minute=0, second=0):
    return dt(year, month, day, hour, minute, second, tzinfo=timezone.utc).timestamp()

def assert_vector_similar(a, b, leq, angle_tolerance=5, a_tolerance=50, units=""):
    ua = a / np.linalg.norm(a)
    ub = b / np.linalg.norm(b)
    angle = np.arccos(np.dot(ua, ub)) * 180 / np.pi
    dif = np.linalg.norm(a - b)
    leq(angle, angle_tolerance,
        f"Exceeded the {angle_tolerance}° tolerance\n ref: {b}\n ours:   {a}\n diff:   {b - a}")
    leq(
        dif, a_tolerance, f"Exceeded the {a_tolerance}{units} tolerance\n ref: {b}\n ours:   {a}\n diff:   {b - a}")
    return angle, dif
