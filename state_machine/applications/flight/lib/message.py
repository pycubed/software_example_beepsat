class Message:
    def __init__(self, priority, str):
        self.priority = priority
        self.header = 0x00
        self.str = bytes(str, 'ascii')

    def packet(self):
        """Returns the byte representation of the message, and if it should be sent with or without ack."""
        pkt = bytearray(len(self.str) + 1)
        pkt[0] = self.header
        pkt[1:] = self.str
        return pkt, True

    def done(self):
        return True

    def ack(self):
        pass

    def no_ack(self):
        pass

    def __lt__(self, other):
        return self.priority < other.priority

    def __le__(self, other):
        return self.priority <= other.priority

    def __eq__(self, other):
        return self.priority == other.priority

    def __ge__(self, other):
        return self.priority >= other.priority

    def __gt__(self, other):
        return self.priority > other.priority

    def __repr__(self) -> str:
        return str(self.str[:20] + "..." if len(self.str) > 23 else self.str)
