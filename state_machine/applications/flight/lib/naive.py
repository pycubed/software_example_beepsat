from lib.message import Message
import lib.radio_headers as headers

class NaiveMessage(Message):

    def __init__(self, priority, str):
        super().__init__(priority, str)
        self.cursor = 0
        self.packet_len = 249  # not 251 because for some reason packet loss is extremely high at this threshold

    def packet(self):
        strng = self.str[self.cursor:self.cursor + self.packet_len]
        pkt = bytearray(len(strng) + 1)
        if len(self.str) <= self.cursor + self.packet_len:  # last packet
            pkt[0] = headers.NAIVE_END
        elif self.cursor == 0:
            pkt[0] = headers.NAIVE_START
        else:
            pkt[0] = headers.NAIVE_MID

        pkt[1:] = strng
        return pkt, True

    def done(self):
        return len(self.str) <= self.cursor

    def ack(self):
        self.cursor += self.packet_len
