from lib.naive import NaiveMessage
import unittest
import sys

sys.path.insert(0, './state_machine/applications/flight')


class NaiveMessageTests(unittest.TestCase):

    def test(self):
        p = NaiveMessage(0, 'x' * 249)
        self.assertEqual(p.packet()[0], 0xfe)
        p.ack()
        self.assertTrue(p.done())
        p = NaiveMessage(0, 'x' * 250)
        self.assertEqual(p.packet()[0], 0xff)
        p.ack()
        self.assertEqual(p.packet()[0], 0xfe)
        p.ack()
        self.assertTrue(p.done())
