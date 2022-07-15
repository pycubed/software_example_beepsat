from lib.message import Message

class NaiveMessage(Message):

    def __init__(self, priority, str):
        super().__init__(priority, str)
        self.cursor = 0
        self.header = 0xff
        self.packet_len = 249  # not 252 because for some reason packet loss is extremely high at this threshold

    def packet(self):
        str = self.str[self.cursor:self.cursor + self.packet_len]
        pkt = bytearray(len(str) + 1)
        pkt[0] = self.header
        pkt[1:] = self.str
        return pkt, True

    def done(self):
        return len(self.str) <= self.cursor

    def ack(self):
        self.cursor += self.packet_len
