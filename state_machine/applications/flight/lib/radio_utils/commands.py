"""Has a bunch of commands that can be called via radio, with an argument.

Contains a dictionary of commands mapping their 2 byte header to a function.
"""

import time
import os
from pycubed import cubesat
from radio_utils import transmission_queue as tq
from radio_utils import headers
from radio_utils.disk_buffered_message import DiskBufferedMessage
from radio_utils.message import Message
import json
import supervisor

NO_OP = b'\x00\x00'
HARD_RESET = b'\x00\x01'
QUERY = b'\x00\x03'
EXEC_PY = b'\x00\x04'
REQUEST_FILE = b'\x00\x05'
LIST_DIR = b'\x00\x06'
TQ_LEN = b'\x00\x07'
MOVE_FILE = b'\x00\x08'
COPY_FILE = b'\x00\x09'
DELETE_FILE = b'\x00\x10'
RELOAD = b'\x00\x11'

def noop(self):
    """No operation"""
    self.debug('no-op')

def hreset(self):
    """Hard reset"""
    self.debug('Resetting')
    cubesat.micro.on_next_reset(cubesat.micro.RunMode.NORMAL)
    cubesat.micro.reset()


def query(task, args):
    """Execute the query as python and return the result"""
    task.debug(f'query: {args}')
    res = str(eval(args))
    _downlink(res)

def exec_py(task, args):
    """Execute the python code, and do not return the result

    :param task: The task that called this function
    :param args: The python code to execute
    :type args: str
    """
    task.debug(f'exec: {args}')
    exec(args)

def request_file(task, file):
    """Request a file to be downlinked

    :param task: The task that called this function
    :param file: The path to the file to downlink
    :type file: str"""
    file = str(file, 'utf-8')
    if file_exists(file):
        tq.push(DiskBufferedMessage(1, file))
    else:
        task.debug(f'File not found: {file}')
        tq.push(Message(9, b'File not found', with_ack=True))

def list_dir(task, path):
    """List the contents of a directory, and downlink the result

    :param task: The task that called this function
    :param path: The path to the directory to list
    :type path: str
    """
    path = str(path, 'utf-8')
    res = os.listdir(path)
    res = json.dumps(res)
    _downlink(res)

def tq_len(task):
    """Return the length of the transmission queue"""
    len = str(tq.len())
    tq.push(Message(1, len))

def move_file(task, args):
    """
    Move a file from source to dest.
    Does not work when moving from sd to flash, should copy files instead.

    :param task: The task that called this function
    :param args: json string [source, dest]
    :type args: str
    """
    try:
        args = json.loads(args)
        os.rename(args[0], args[1])
        task.debug('Sucess moving file')
        tq.push(Message(9, b'Success moving file'))
    except Exception as e:
        task.debug(f'Error moving file: {e}')
        _downlink(f'Error moving file: {e}', priority=9)

def copy_file(task, args):
    """
    Copy a file from source to dest

    :param task: The task that called this function
    :param args: json string [source, dest]
    :type args: str
    """
    try:
        args = json.loads(args)
        with open(args[0], 'rb') as source, open(args[1], 'wb') as dest:
            _cp(source, dest)
        task.debug('Sucess copying file')
        tq.push(Message(9, b'Success copying file'))
    except Exception as e:
        task.debug(f'Error moving file: {e}')
        _downlink(f'Error moving file: {e}', priority=9)

def delete_file(task, file):
    """Delete file

    :param task: The task that called this function
    :param file: The path to the file to delete
    :type file: str
    """
    try:
        os.remove(file)
        tq.push(Message(9, b'Success deleting file'))
    except Exception as e:
        task.debug(f'Error deleting file: {e}')
        _downlink(f'Error deleting file: {e}', priority=9)

async def reload(task):
    """Reloads the flight software

    :param task: The task that called this function
    """
    task.debug('Reloading')
    msg = bytearray([headers.DEFAULT])
    msg.append(b'reset')
    await cubesat.radio.send(data=msg)
    supervisor.reload()


"""
HELPER FUNCTIONS
"""

def _downlink(data, priority=1):
    """Write data to a file, and then create a new DiskBufferedMessage to downlink it"""
    fname = f'/sd/downlink/{time.monotonic_ns()}.txt'
    if not file_exists('/sd/downlink'):
        os.mkdir('/sd/downlink')
    f = open(fname, 'w')
    f.write(data)
    f.close()
    tq.push(DiskBufferedMessage(priority, fname))

def _cp(source, dest, buffer_size=1024):
    """
    Copy a file from source to dest. source and dest
    must be file-like objects, i.e. any object with a read or
    write method, like for example StringIO.
    """
    while True:
        copy_buffer = source.read(buffer_size)
        if not copy_buffer:
            break
        dest.write(copy_buffer)

def file_exists(path):
    try:
        os.stat(path)
        return True
    except Exception:
        return False


commands = {
    NO_OP: noop,
    HARD_RESET: hreset,
    QUERY: query,
    EXEC_PY: exec_py,
    REQUEST_FILE: request_file,
    LIST_DIR: list_dir,
    TQ_LEN: tq_len,
    MOVE_FILE: move_file,
    COPY_FILE: copy_file,
    DELETE_FILE: delete_file,
    RELOAD: reload,
}

command_name_map = {
    "NO_OP": [NO_OP, False],
    "HARD_RESET": [HARD_RESET, False],
    "QUERY": [QUERY, True],
    "EXEC_PY": [EXEC_PY, False],
    "REQUEST_FILE": [REQUEST_FILE, True],
    "LIST_DIR": [TQ_LEN, True],
    "TQ_LEN": [TQ_LEN, True],
    "MOVE_FILE": [MOVE_FILE, True],
    "COPY_FILE": [COPY_FILE, True],
    "DELETE_FILE": [DELETE_FILE, True],
    "RELOAD": [RELOAD, True],
}

super_secret_code = b'p\xba\xb8C'
