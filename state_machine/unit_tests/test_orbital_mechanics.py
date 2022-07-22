from unicodedata import digit
import unittest
import sys
import math
from numpy import array
from numpy.linalg import norm

sys.path.insert(0, './state_machine/applications/flight')


from lib.orbital_mechanics import rk4, propogate

class TestRK4(unittest.TestCase):

    def test_basic_difeqs(self):
        self.assertAlmostEqual(rk4(0, 0.1, math.exp), 0.105360515657833149)
        self.assertAlmostEqual(rk4(1, 0.1, lambda x: 3 * x), 1.349859, places=4)

    def test_orbit_doesnt_crash(self):
        """Tests if this probably stable orbit doesn't crash into the earth"""
        x = array([0, 0, 10000.0, 5, -5, 0])
        for _ in range(20):
            x = propogate(x, 60 * 60 * 24, integration_step=60)
            self.assertGreaterEqual(norm(x[0:3]), 6371.009)


x = TestRK4()
x.test_orbit()
