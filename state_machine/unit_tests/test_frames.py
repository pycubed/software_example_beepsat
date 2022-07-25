import unittest
import sys
from numpy import array, testing

sys.path.insert(0, './state_machine/applications/flight')

import lib.frames as frames

class TestECIToECF(unittest.TestCase):

    def test_no_changes(self):
        testing.assert_array_almost_equal(
            array([[0.34494635,  -0.9386224,    0.0],
                   [0.9386224,    0.34494635,   0.0],
                   [0.0,          0.0,          1.0]]),
            frames.eci_to_ecef(1658768897),
            decimal=3
        )
        testing.assert_array_almost_equal(
            array([[0.36104087,  -0.93254999,   0.0],
                   [0.93254999,   0.36104087,   0.0],
                   [0.0,          0.0,          1.0]]),
            frames.eci_to_ecef(1658768897 + 86400),
            decimal=3
        )


x = TestECIToECF()
x.test_no_changes()
