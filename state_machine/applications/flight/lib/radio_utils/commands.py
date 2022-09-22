import time
import os
from pycubed import cubesat
from radio_utils import transmission_queue as tq
from radio_utils import headers
from radio_utils.chunk import ChunkMessage
from radio_utils.message import Message
import json

NO_OP = b'\x00\x00'
HARD_RESET = b'\x00\x01'
QUERY = b'\x00\x03'
EXEC_PY = b'\x00\x04'
REQUEST_FILE = b'\x00\x05'
LIST_DIR = b'\x00\x06'
TQ_LEN = b'\x00\x07'

def noop(self):
    self.debug('no-op')

async def hreset(self):
    self.debug('Resetting')
    msg = bytearray([headers.DEFAULT])
    msg.append(b'reset')
    await cubesat.radio.send(data=msg)
    cubesat.micro.on_next_reset(self.cubesat.micro.RunMode.NORMAL)
    cubesat.micro.reset()


def query(task, args):
    task.debug(f'query: {args}')
    res = str(eval(args))
    downlink(res)

def exec_py(task, args):
    task.debug(f'exec: {args}')
    exec(args)

def request_file(task, file):
    file = str(file, 'utf-8')
    try:
        os.stat(file)
        tq.push(ChunkMessage(1, file))
    except Exception:
        task.debug(f'File not found: {file}')
        tq.push(Message(9, b'File not found', with_ack=True))

def list_dir(task, path):
    path = str(path, 'utf-8')
    res = os.listdir(path)
    res = json.dumps(res)
    downlink(res)

def tq_len(task):
    len = str(tq.len())
    tq.push(Message(1, len))

# Helper functions

def downlink(data, priority=1):
    fname = f'/sd/downlink/{time.monotonic_ns()}.txt'
    f = open(fname, 'w')
    f.write(data)
    f.close()
    tq.push(ChunkMessage(priority, fname))


commands = {
    NO_OP: noop,
    HARD_RESET: hreset,
    QUERY: query,
    EXEC_PY: exec_py,
    REQUEST_FILE: request_file,
    LIST_DIR: list_dir,
    TQ_LEN: tq_len,
}
