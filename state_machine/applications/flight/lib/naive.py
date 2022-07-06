from lib.message import Message

class NaiveMessage(Message):

    def __init__(self, priority, str):
        super().__init__(priority, str)
        self.cursor = 0
        self.packet_len = 250  # not 252 because for some reason packet loss is extremely high at this threshold

    def packet(self):
        return self.str[self.cursor:self.cursor + self.packet_len], True

    def done(self):
        return len(self.str) == self.cursor

    def ack(self):
        self.cursor += self.packet_len
