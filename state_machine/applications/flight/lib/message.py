class Message:
    def __init__(self, key, string):
        self.key = key
        self.string = ''

    def packet(self):
        return self.string

    def __lt__(self, other):
        return self.key < other.key

    def __le__(self, other):
        return self.key <= other.key

    def __eq__(self, other):
        return self.key == other.key

    def __gt__(self, other):
        return self.key > other.key

    def __ge__(self, other):
        return self.key >= other.key
