from lib.message import Message
import lib.radio_headers as headers

class NaiveMessage(Message):

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
