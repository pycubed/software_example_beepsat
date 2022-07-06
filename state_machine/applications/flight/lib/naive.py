from lib.message import Message

class NaiveMessage(Message):

    def __init__(self, priority, str):
        super().__init__(priority, str)
        self.cursor = 0

    def packet(self):
        return self.str[self.cursor:self.cursor + 250], True

    def done(self):
        return len(self.str) == self.cursor

    def ack(self):
        self.cursor += 250
