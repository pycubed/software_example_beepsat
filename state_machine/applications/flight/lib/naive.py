from lib.message import Message

class NaiveMessage(Message):
    """Transmits the message 249 bytes at a time.
    Sets special headers for the first packet, middle packets, and last packet.

    :param priority: The priority of the message (higher is better)
    :type priority: int
    :param str: The message to send
    :type str: str
    """

    def __init__(self, priority, str):
        super().__init__(priority, str)
        self.cursor = 0
        self.header = 0xff
        self.packet_len = 249  # not 251 because for some reason packet loss is extremely high at this threshold

    def packet(self):
        strng = self.str[self.cursor:self.cursor + self.packet_len]
        pkt = bytearray(len(strng) + 1)
        pkt[0] = self.header
        if len(self.str) <= self.cursor + self.packet_len:  # last packet
            pkt[0] = 0xfe
        pkt[1:] = strng
        return pkt, True

    def done(self):
        return len(self.str) <= self.cursor

    def ack(self):
        self.cursor += self.packet_len
