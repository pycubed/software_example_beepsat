from .message import Message
from . import headers

class NaiveMessage(Message):
    """Transmits the message 249 bytes at a time.
    Sets special headers for the first packet, middle packets, and last packet.

    :param priority: The priority of the message (higher is better)
    :type priority: int
    :param str: The message to send
    :type str: str | bytes | bytearray
    """

    packet_len = 249  # not 251 because for some reason packet loss is extremely high at this threshold

    def __init__(self, priority, str):
        super().__init__(priority, str)
        self.cursor = 0

    def packet(self):
        payload = self.str[self.cursor:self.cursor + self.packet_len]
        pkt = bytearray(len(payload) + 1)
        if len(self.str) <= self.cursor + self.packet_len:  # last packet
            pkt[0] = headers.NAIVE_END
        elif self.cursor == 0:
            pkt[0] = headers.NAIVE_START
        else:
            pkt[0] = headers.NAIVE_MID

        pkt[1:] = payload
        return pkt, True

    def done(self):
        return len(self.str) <= self.cursor

    def ack(self):
        self.cursor += self.packet_len
