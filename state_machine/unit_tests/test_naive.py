from struct import pack
import unittest
import sys

sys.path.insert(0, './state_machine/applications/flight')

from lib.naive import NaiveMessage
import lib.radio_headers as headers

class NaiveMessageTests(unittest.TestCase):

    def test(self):
        packet_len = 249

        p = NaiveMessage(0, 'x' * packet_len)
        res, _ = p.packet()
        self.assertEqual(res[0], headers.NAIVE_END)
        p.ack()
        self.assertTrue(p.done())

        p = NaiveMessage(0, 'x' * (packet_len + 1))
        res, _ = p.packet()
        self.assertEqual(res[0], headers.NAIVE_START)
        p.ack()
        res, _ = p.packet()
        self.assertEqual(res[0], headers.NAIVE_END)
        p.ack()
        self.assertTrue(p.done())

        p = NaiveMessage(0, 'x' * (packet_len * 2 + 1))
        res, _ = p.packet()
        self.assertEqual(res[0], headers.NAIVE_START)
        p.ack()
        res, _ = p.packet()
        self.assertEqual(res[0], headers.NAIVE_MID)
        p.ack()
        self.assertFalse(p.done())
        res, _ = p.packet()
        self.assertEqual(res[0], headers.NAIVE_END)
        p.ack()
        self.assertTrue(p.done())
