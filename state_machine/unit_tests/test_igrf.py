import unittest
import sys
from datetime import datetime as dt, timezone
import numpy as np

sys.path.insert(0, './state_machine/applications/flight')

from lib.IGRF import igrf, igrf_eci

def timestamp(year, month, day, hour=0, minute=0, second=0):
    return dt(year, month, day, hour, minute, second, tzinfo=timezone.utc).timestamp()

def assert_vector_almost_equal(a, b, assertLessEqual, angle_tolerance=5, nt_tolerance=3000):
    ua = a / np.linalg.norm(a)
    ub = b / np.linalg.norm(b)
    angle = np.arccos(np.dot(ua, ub)) * 180 / np.pi
    dif = np.linalg.norm(a - b)
    assertLessEqual(angle, angle_tolerance,
                    f"Exceeded the {angle_tolerance}° tolerance\n IGRF13: {b}\n ours:   {a}\n diff:   {b - a}")
    assertLessEqual(
        dif, nt_tolerance, f"Exceeded the {nt_tolerance} nT tolerance\n IGRF13: {b}\n ours:   {a}\n diff:   {b - a}")


EARTH_RADIUS = 6.378136300e3  # km


class IGRF(unittest.TestCase):

    def test_matches_IGRF13(self):
        # test data generated from https://www.ngdc.noaa.gov/IAGA/vmod/igrf.html
        # using pyIGRF.py
        # Note that we use geocentric coordinates
        # We are comparing the results with the IGRF13 results
        t = dt(2020, 4, 19, 15, tzinfo=timezone.utc).timestamp()  # time is about 2020.3
        assert_vector_almost_equal(
            igrf(t, 34.567, 45.678, 6697.043115),
            [24354.4, 1908.4, 32051.6],
            self.assertLessEqual
        )

        t = dt(2023, 1, 1, tzinfo=timezone.utc).timestamp()
        assert_vector_almost_equal(
            igrf(t, -12, 37, 6700),
            [20274.2, -1994.6, -18852.8],
            self.assertLessEqual
        )

        t = dt(2022, 7, 2, 22, tzinfo=timezone.utc).timestamp()
        assert_vector_almost_equal(
            igrf(t, 25, 35, EARTH_RADIUS + 400),  # about the ISS altitude
            [28295.864360612726, 1850.2071187341612, 21436.550334577572],
            self.assertLessEqual,
        )

        t = dt(2023, 1, 1, tzinfo=timezone.utc).timestamp()
        assert_vector_almost_equal(
            igrf(t, -79, 48, EARTH_RADIUS + 700),
            [4650.9, -10831.9, -34896.3],
            self.assertLessEqual,
        )

    def test_no_changes(self):
        """Test that our changes to the IGRF model do not change the results."""
        equal = np.testing.assert_array_almost_equal

        t = dt(2020, 4, 19, 15, tzinfo=timezone.utc).timestamp()
        equal(
            igrf(t, 34.567, 45.678, 6697.043115),
            [24694.17511877, 2125.5475454, 32160.37154219],
            decimal=1
        )

        t = dt(2021, 7, 28, 2, tzinfo=timezone.utc).timestamp()
        equal(
            igrf(t, -12, 127, 6873),
            [28092.523258, 1432.59565072, -22804.66673182],
            decimal=1
        )

class IGRF_ECI(unittest.TestCase):

    def test_close_GN(self):
        """Test that our IGRF in ECI coordinates is close to the results from GravNav.
        Source: https://github.com/RoboticExplorationLab/GravNav/blob/main/simple_sim/mag_field.jl#L6"""
        angle_tolerance = 1
        nt_tolerance = 30
        t = timestamp(2020, 9, 15)
        assert_vector_almost_equal(
            igrf_eci(t, [7000, 7500, 9300]),
            [-2958.36063183389, -3285.782343814322, -751.7865862535493],
            self.assertLessEqual,
            angle_tolerance,
            nt_tolerance
        )

        t = timestamp(2021, 4, 1)
        assert_vector_almost_equal(
            igrf_eci(t, [7654, -12345, 5678]),
            [-963.4031953585253, 1522.7638883411967, 1657.0123037449737],
            self.assertLessEqual,
            angle_tolerance,
            nt_tolerance
        )

        t = timestamp(2020, 8, 13)
        assert_vector_almost_equal(
            igrf_eci(t, [8763, -7421, -9213]),
            [1978.9330574152757, -2226.2182265227348, -306.67003898572216],
            self.assertLessEqual,
            angle_tolerance,
            nt_tolerance
        )
