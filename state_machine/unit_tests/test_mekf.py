import unittest
import sys
from numpy import testing, array

sys.path.insert(0, './state_machine/applications/flight')

from lib.mekf import propagate_state  # noqa: E402

class PropogationTest(unittest.TestCase):

    def test(self):
        expect = array([[0.5931645151518956, 0.42554207999942495, 0.5398640677185691, 0.41906632470378713]]).transpose()
        testing.assert_almost_equal(
            expect,
            propagate_state(
                array([[0.5, 0.5, 0.5, 0.5]]).transpose(),
                array([[0.324, 0.24, 0.9]]).transpose(),
                array([[0.23, 0.12, 0.321]]).transpose(),
                0.5
            )
        )
