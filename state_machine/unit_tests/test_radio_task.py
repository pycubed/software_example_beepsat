import sys
from unittest import IsolatedAsyncioTestCase

sys.path.insert(0, './state_machine/drivers/emulation/lib')
sys.path.insert(0, './state_machine/applications/flight')
sys.path.insert(0, './state_machine/applications/flight/lib')
sys.path.insert(0, './state_machine/frame/')

import Tasks.radio as radio
from radio_driver import _Packet as Packet
import radio_utils.headers as headers
import radio_utils.commands as cdh
from pycubed import cubesat
from state_machine import state_machine

radio.ANTENNA_ATTACHED = True
state_machine.state = 'Debug'

def command_data(command_code, args):
    return bytes([headers.COMMAND]) + b'p\xba\xb8C' + command_code + args

class AssertCalled:

    def __init__(self, func):
        self.func = func
        self.called = False

    def command(self, s2, args=None):
        self.called = True
        if args is None:
            self.func(s2)
        else:
            self.func(s2, args)

class RXCommandTest(IsolatedAsyncioTestCase):

    async def test(self):
        """Test that RX of a command with and without args works"""
        rt = radio.task()
        cdh._downlink = lambda x: None  # Don't try to downlink results of command

        noop_packet = Packet(command_data(cdh.NO_OP, b''))
        cubesat.radio._push_rx_queue(noop_packet)
        noop = AssertCalled(cdh.noop)
        cdh.commands[cdh.NO_OP] = noop.command
        await rt.main_task()
        self.assertEqual(noop.called, True, "No-op command was not called")

        query_packet = Packet(command_data(cdh.QUERY, b'5+5'))
        cubesat.radio._push_rx_queue(query_packet)
        query = AssertCalled(cdh.query)
        cdh.commands[cdh.QUERY] = query.command
        await rt.main_task()
        self.assertEqual(noop.called, True, "Query command was not called")
