import unittest
import sys

sys.path.insert(0, './state_machine/applications/flight/lib/')

from radio_utils.naive import NaiveMessage
import radio_utils.headers as headers

packet_len = NaiveMessage.packet_len

class NaiveMessageTests(unittest.TestCase):

    def test_short_message(self):
        """Tests that a 1 packet message has the correct headers"""

        p = NaiveMessage(0, 'x' * packet_len)
        res, _ = p.packet()
        self.assertEqual(res[0], headers.NAIVE_END)
        p.ack()
        self.assertTrue(p.done())

    def test_medium_message(self):
        """Tests that a 2 packet message has the correct headers for each packet"""

        p = NaiveMessage(0, 'x' * (packet_len + 1))
        res, _ = p.packet()
        self.assertEqual(res[0], headers.NAIVE_START)
        p.ack()
        res, _ = p.packet()
        self.assertEqual(res[0], headers.NAIVE_END)
        p.ack()
        self.assertTrue(p.done())

    def test_long_message(self):
        """Tests that a 3 packet message has the correct headers for each packet"""
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
