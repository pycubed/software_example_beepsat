import unittest
import sys

sys.path.insert(0, './state_machine/applications/flight')

from lib.naive import NaiveMessage

class NaiveMessageTests(unittest.TestCase):

    def test(self):
        p = NaiveMessage(0, 'x' * 249)
        res, _ = p.packet()
        self.assertEqual(res[0], 0xfe)
        p.ack()
        self.assertTrue(p.done())
        p = NaiveMessage(0, 'x' * 250)
        res, _ = p.packet()
        self.assertEqual(res[0], 0xff)
        p.ack()
        res, _ = p.packet()
        self.assertEqual(res[0], 0xfe)
        p.ack()
        self.assertTrue(p.done())
