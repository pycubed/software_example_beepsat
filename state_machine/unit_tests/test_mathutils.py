import unittest
import sys
from numpy import testing, array

sys.path.insert(0, './state_machine/applications/flight')

from lib.mathutils import hat  # noqa: E402

class HatTests(unittest.TestCase):

    def test(self):
        testing.assert_equal(
            array(
                [[0,  -3,  2],
                 [3, 0,  -1],
                 [-2,  1, 0]]),
            hat([1, 2, 3])
        )
        testing.assert_equal(
            array(
                [[0.0,  -0.6, 0.4],
                 [0.6,  0.0,  -0.3],
                 [-0.4, 0.3,  0.0]]),
            hat([0.3, 0.4, 0.6])
        )
