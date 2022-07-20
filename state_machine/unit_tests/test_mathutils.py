import unittest
import sys
from numpy import testing, array, zeros, eye, ones

sys.path.insert(0, './state_machine/applications/flight')

from lib.mathutils import hat, quaternion_to_left_matrix, block  # noqa: E402

def col(arr):
    return array([arr]).transpose()

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
        self.assertRaises(ValueError, hat, [1, 2, 3, 4])
        testing.assert_equal(
            array([[0.0, 0.3982060297895143, 0.2543322132742208],
                   [-0.3982060297895143, 0.0, -0.7083212680159963],
                   [-0.2543322132742208, 0.7083212680159963, 0.0]]),
            hat(array([[0.7083212680159963, 0.2543322132742208, -0.3982060297895143]]).transpose())
        )

class blockTests(unittest.TestCase):

    def test(self):
        a = array([[1, 1]])
        b = array([[2]])
        c = array(
            [[3, 3],
             [3, 3],
             [3, 3]])
        d = array(
            [[4],
             [4],
             [4]])
        testing.assert_equal(
            block([[a, b], [c, d]]),
            array([[1, 1, 2],
                   [3, 3, 4],
                   [3, 3, 4],
                   [3, 3, 4]])
        )
        a = zeros((2, 3))
        b = eye(2) * 2
        c = eye(3) * 5
        d = ones((3, 2))
        testing.assert_equal(
            block([[a, b], [c, d]]),
            array([[0, 0, 0, 2, 0],
                   [0, 0, 0, 0, 2],
                   [5, 0, 0, 1, 1],
                   [0, 5, 0, 1, 1],
                   [0, 0, 5, 1, 1]])
        )

class QuaternionToLeftTests(unittest.TestCase):

    def test(self):
        q = array([0.692, -0.332,  0.499,  0.403])
        testing.assert_almost_equal(
            array(
                [[0.692,   0.332,  -0.499,  -0.403],
                 [-0.332,  0.692,  -0.403,   0.499],
                 [0.499,   0.403,   0.692,   0.332],
                 [0.403,  -0.499,  -0.332,   0.692]]),
            quaternion_to_left_matrix(q)
        )
        q = array([[0.5, 0.5, 0.5, 0.5]]).transpose()
        testing.assert_equal(
            array(
                [[0.5,  -0.5,  -0.5,  -0.5],
                 [0.5,   0.5,  -0.5,   0.5],
                 [0.5,   0.5,   0.5,  -0.5],
                 [0.5,  -0.5,   0.5,   0.5]]),
            quaternion_to_left_matrix(q)
        )
        q = array([[-0.5244311817641283, 0.7083212680159963, 0.2543322132742208, -0.3982060297895143]]).transpose()
        testing.assert_almost_equal(
            array([[-0.524431, -0.708321, -0.254332, 0.398206],
                   [0.708321, -0.524431, 0.398206, 0.254332],
                   [0.254332, -0.398206, -0.524431, -0.708321],
                   [-0.398206, -0.254332, 0.708321, -0.524431]]),
            quaternion_to_left_matrix(q),
            decimal=6
        )
