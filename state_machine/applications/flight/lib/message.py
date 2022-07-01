class Message:
    def __init__(self, priority, str):
        self.priority = priority
        self.str = str

    def packet(self):
        return bytes(self.str, 'utf-8'), True

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
        return self.str[:20] + "..." if len(self.str) > 23 else self.str
