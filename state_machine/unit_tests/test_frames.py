import unittest
import sys
from numpy import array, cos, sin, pi
from numpy.linalg import norm

sys.path.insert(0, './state_machine/applications/flight')

import lib.frames as frames

EARTH_RADIUS = 6371  # Earth radius (km)
LEO = 2000  # Low Earth Orbit Altitude Limit (km)

def sphere(r, theta, phi):
    return array([r * cos(phi) * sin(theta), r * sin(phi) * sin(theta), r * cos(theta)])

def assert_matrices_close(A, B, limit=40):
    """Assert that the matrices are close enough to be considered equal.
    This is quantified by ||Ax - Bx|| <= limit where limit=40km by default.
    With 20 randomly preselected x vectors.
    """
    random_r = [0.8024612835524245, 0.7799976069168522, 0.2755708484874475, 0.7330229027509386, 0.25907330462717226,
                0.5463115713496455, 0.44071908096464074, 0.6813197448495494, 0.6643272512636399, 0.17347325364175925,
                0.8755423550584049, 0.4144062746589813, 0.574574071973453, 0.5450505615416308, 0.898767242216612,
                0.8929993117314708, 0.13563822268349823, 0.30579939151778357, 0.22185382634541484, 0.7369055233784879]
    random_theta = [0.5101178853945276, 0.335573508966745, 0.7898993563976668, 0.4379619702634009, 0.3317991172264475,
                    0.05409153128430766, 0.2089447958278125, 0.16700392301892353, 0.4026595634137289, 0.804533000884362,
                    0.5775769675013817, 0.4915534196831799, 0.3488173952232939, 0.41138992770355287, 0.2074700298578479,
                    0.9443597528619022, 0.4369826508351583, 0.9187908118163634, 0.13584368379659217, 0.8920158527647813]
    random_phi = [0.9331083038111837, 0.171456982916933, 0.9973850770496011, 0.09646857671696607, 0.914755982365568,
                  0.989740039777413, 0.34836908993688587, 0.9804857522697122, 0.16912940409029054, 0.8737226962320032,
                  0.48253924423095496, 0.8906909282328218, 0.5755947594709588, 0.6020846507401795, 0.1756451335479995,
                  0.28715487506952453, 0.04206276596303382, 0.4749591026605633, 0.599812282465087, 0.8555165321413011]
    # generate random vectors

    def gen_vector(r, theta, phi):
        return array([
            (r / 2 + 0.5) * (EARTH_RADIUS + LEO),
            theta * 2 * pi,
            phi * 2 * pi
        ])

    rx = [gen_vector(random_r[i], random_theta[i], random_phi[i]) for i in range(20)]

    maxdif = 0.0
    for x in rx:
        dist = norm(A @ x - B @ x)
        maxdif = max(maxdif, dist)
        assert dist <= limit, f"Matrices are not close enough.\n||Ax - Bx|| = {int(dist)}km\nA={A}\nB={B}"
    print(f"max(||Ax - Bx||) = {int(maxdif)}km")


class TestECIToECF(unittest.TestCase):

    def test_similar_to_SD(self):
        """Test that our ECI to ECF transformation is similar enough to the Satellite Dynamics implementation.
        Note that for these test cases the max error was 27km."""
        from datetime import datetime as dt, timezone

        t = dt(2000, 1, 1, tzinfo=timezone.utc).timestamp()
        A = array([[-0.170822,    0.985302,     2.31292e-5],
                   [-0.985302,   -0.170822,    -3.32888e-5],
                   [-2.88486e-5, -2.84757e-5,   1.0]])
        assert_matrices_close(A, frames.eci_to_ecef(t))

        t = dt(2023, 3, 5, tzinfo=timezone.utc).timestamp()
        A = array([[-0.952589,    0.304254,   0.00202102],
                   [-0.304253,   -0.952591,   0.000667447],
                   [0.00212828,  2.09018e-5, 0.999998]])
        assert_matrices_close(A, frames.eci_to_ecef(t))

        t = dt(2023, 4, 1, tzinfo=timezone.utc).timestamp()
        A = array([[-0.98863,     -0.15035,     0.00221924],
                   [0.15035,      -0.988633,   -0.000306172],
                   [0.00224005,    3.0972e-5,   0.999997]])
        assert_matrices_close(A, frames.eci_to_ecef(t))

        t = dt(2023, 8, 24, tzinfo=timezone.utc).timestamp()
        A = array([[0.881403,   -0.47236,   -0.0019064],
                   [0.472359,    0.881406,  -0.00105366],
                   [0.00217802,  2.8192e-5,  0.999998]])
        assert_matrices_close(A, frames.eci_to_ecef(t))


x = TestECIToECF()
x.test_similar_to_SD()
