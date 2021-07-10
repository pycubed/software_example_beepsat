import time

commands = {
    b'\x8eb': 'no-op',
    b'\xd4\x9f': 'hreset',
    b'8\x93': 'query',
    b'\x12\x06': 'shutdown',
}

########### commands without arguments ###########
def noop(self):
    self.debug('no-op')
    pass

def hreset(self):
    self.debug('Resetting')
    try:
        self.cubesat.radio1.send(data=b'resetting')
    except:
        pass

########### commands with arguments ###########
def query(self,args):
    self.debug('query: {}'.format(args))
    self.cubesat.radio1.send(data=str(eval(args)))

def shutdown(self,args):
    # make shutdown require yet another pass-code
    if args == b'\x0b\xfdI\xec':
        self.debug('valid shutdown command received')
        # set shutdown NVM bit flag
        self.cubesat.f_shtdwn=True
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






