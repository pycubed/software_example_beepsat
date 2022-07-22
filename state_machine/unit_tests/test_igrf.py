import unittest
import sys
import datetime
import numpy as np

sys.path.insert(0, './state_machine/applications/flight')

from lib.IGRF2 import igrf as igrflib

def assert_almost_same(a, b, assertLessEqual):
    print(a, b)
    ua = a / np.linalg.norm(a)
    ub = b / np.linalg.norm(b)
    angle = np.arccos(np.dot(ua, ub)) * 180 / np.pi
    dif = np.linalg.norm(a - b)
    assertLessEqual(angle, 5)
    assertLessEqual(dif, 500, f"Exceeded the 500nT tolerance\n IGRF13: {b}\n ours:   {a}\n diff:   {b - a}")


class IGRFTests(unittest.TestCase):

    def test(self):
        # test data generated from https://www.ngdc.noaa.gov/IAGA/vmod/igrf.html
        # using pyIGRF.py
        # Note that we use geocentric coordinates
        dt = datetime.datetime
        igrf = igrflib.ned_igrf
        EARTH_RADIUS = 3485  # km
        t = dt(2020, 4, 19, 15).timestamp()  # time is about 2020.3
        assert_almost_same(
            igrf(t, 34.567, 45.678, 6697.043115),
            [24354.4, 1908.4, 32051.6],
            self.assertLessEqual
        )

    def test_no_changes(self):
        pass

x = IGRFTests()
x.test()