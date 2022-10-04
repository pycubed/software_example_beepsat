from .message import Message
from . import headers
from . import MAX_PACKET_LEN
import os

class ChunkMessage(Message):
    """Transmits the message 251 bytes at a time.
    Sets special headers for the first packet, middle packets, and last packet.
    Reads from a file one chunk at a time.

    :param priority: The priority of the message (higher is better)
    :type priority: int
    :param path: The path to the file containing the message to send
    :type str: str | bytes | bytearray
    """

    packet_len = MAX_PACKET_LEN - 1

    def __init__(self, priority, path):
        self.cursor = 0
        self.priority = priority
        self.path = path
        self.msg_len = os.stat(path)[6]

    def packet(self):
        """Reads the next chunk of data from sd, and returns this is a packet.
        Always requests an ack."""
        try:
            with open(self.path, "rb") as f:
                f.seek(self.cursor)
                payload = f.read(self.packet_len)
        except Exception as e:
            print(f'Error reading file {self.path}: {e}')
        pkt = bytearray(len(payload) + 1)
        if self.msg_len <= self.cursor + self.packet_len:  # last packet
            pkt[0] = headers.CHUNK_END
        elif self.cursor == 0:
            pkt[0] = headers.CHUNK_START
        else:
            pkt[0] = headers.CHUNK_MID

        pkt[1:] = payload
        return pkt, True

    def done(self):
        return self.msg_len <= self.cursor

    def ack(self):
        self.cursor += self.packet_len

    def __repr__(self) -> str:
        return f'<Chunk: {self.path}>'
