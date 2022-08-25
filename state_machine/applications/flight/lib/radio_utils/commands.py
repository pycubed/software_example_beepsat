import time
from lib.pycubed import cubesat

NO_OP = b'\x00\x00'
HARD_RESET = b'\x00\x01'
SHUTDOWN = b'\x00\x02'
QUERY = b'\x00\x03'
EXEC_PY = b'\x00\x04'

def noop(self):
    self.debug('no-op')
    pass

def hreset(self):
    self.debug('Resetting')
    cubesat.radio1.send(data=b'resetting')
    cubesat.micro.on_next_reset(self.cubesat.micro.RunMode.NORMAL)
    cubesat.micro.reset()


def shutdown(self, args):
    # make shutdown require yet another pass-code
    if args == b'\x0b\xfdI\xec':
        self.debug('valid shutdown command received')
        # set shutdown NVM bit flag
        self.cubesat.f_shtdwn = True
        # stop all tasks
        for t in self.cubesat.scheduled_tasks:
            self.cubesat.scheduled_tasks[t].stop()
        self.cubesat.powermode('minimum')

        """
        Exercise for the user:
            Implement a means of waking up from shutdown
            See beep-sat guide for more details
            https://pycubed.org/resources
        """
        while True:
            time.sleep(100000)

def query(self, args):
    self.debug(f'query: {args}')
    self.cubesat.radio1.send(data=str(eval(args)))

def exec_py(self, args):
    self.debug(f'exec: {args}')
    exec(args)


commands = {
    NO_OP: noop,
    HARD_RESET: hreset,
    SHUTDOWN: shutdown,
    QUERY: query,
    EXEC_PY: exec_py,
}
