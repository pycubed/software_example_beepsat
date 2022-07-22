import unittest
import sys
import datetime

sys.path.insert(0, './state_machine/applications/flight')

from lib.IGRF2 import igrf as igrflib


class IGRFTests(unittest.TestCase):

    def test(self):
        dt = datetime.datetime
        igrf = igrflib.ned_igrf
        r = igrf(dt(2022, 7, 22).timestamp(), 64, -148, 100)
        print(r)
        r = igrf(dt(2022, 7, 22).timestamp(), 34.567, 45.678, 100)
        print(r)
        r = igrf(dt(2020, 3, 5).timestamp(), 34.567, 45.678, 100)
        print(r)
        r = igrf(dt(2021, 1, 1).timestamp(), 34.567, 45.678, 100)
        print(r)


x = IGRFTests()
x.test()
