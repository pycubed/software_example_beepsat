"""
Radio Task:

Manages all radio communication for the cubesat.
"""
from lib.template_task import Task
import radio_utils.transmission_queue as tq
import radio_utils.commands as cdh
import radio_utils.headers as headers
from pycubed import cubesat

ANTENNA_ATTACHED = False

def should_transmit():
    """
    Return if we should transmit
    """
    return ANTENNA_ATTACHED and not tq.empty()

class task(Task):
    name = 'radio'
    color = 'teal'
    super_secret_code = b'p\xba\xb8C'

    def __init__(self):
        super().__init__()
        self.msg = bytes([])
        self.cmsg_last = None
        self.msg_last = None

    async def main_task(self):
        """
        Manages all RF communications for the satelite.

        In order to transmit something one should push to the transmission queue.
        """
        if not cubesat.radio:
            self.debug('No radio attached, skipping radio task')
            return
        elif not ANTENNA_ATTACHED:
            self.debug('No antenna attached, skipping radio task')
            return

        if should_transmit():
            msg = tq.peek()
            packet, with_ack = msg.packet()
            self.debug(f'Transmission Queue {tq.queue}')

            debug_packet = str(packet)[:20] + "...." if len(packet) > 23 else packet
            self.debug(f"Sending packet: {debug_packet}")

            if with_ack:
                if await cubesat.radio.send_with_ack(packet):
                    msg.ack()
                else:
                    msg.no_ack()
            else:
                await cubesat.radio.send(packet, keep_listening=True)

            if tq.peek().done():
                tq.pop()
        else:
            self.debug("No packets to send")
            response = await cubesat.radio.receive(
                keep_listening=True,
                with_ack=ANTENNA_ATTACHED,
                with_header=False,
                timeout=10)
            if response is not None:
                cubesat.f_contact = True
                header = response[0]
                response = response[1:]  # remove the header byte

                self.debug(f'Recieved msg "{response}", ' +
                           f'RSSI: {cubesat.radio.last_rssi}, ' +
                           f'FEI: {cubesat.radio.frequency_error}')

                if (header == headers.MEMORY_BUFFERED_START or
                        header == headers.MEMORY_BUFFERED_MID or
                        header == headers.MEMORY_BUFFERED_END):
                    self.handle_memory_buffered_message(header, response)
                elif (header == headers.DISK_BUFFERED_START or
                        header == headers.DISK_BUFFERED_MID or
                        header == headers.DISK_BUFFERED_END):
                    self.handle_disk_buffered_message(header, response)
                elif header == headers.COMMAND:
                    await self.handle_command(response)
            else:
                self.debug('No packets received')

    def handle_memory_buffered_message(self, header, response):
        """Handler function for the memory_buffered_message message type"""
        if header == headers.MEMORY_BUFFERED_START:
            self.msg = response
        else:
            if response != self.msg_last:
                self.msg += response
            else:
                self.debug('Repeated chunk')
        self.msg_last = response

        if header == headers.MEMORY_BUFFERED_END:
            self.msg_last = None
            self.msg = str(self.msg, 'utf-8')

    async def handle_command(self, response):
        """Handler function for commands"""
        if len(response) < 6 or response[:4] != self.super_secret_code:
            return

        cmd = bytes(response[4:6])  # [pass-code(4 bytes)] [cmd 2 bytes] [args]
        cmd_args = bytes(response[6:])
        try:
            self.debug(f'cmd args: {cmd_args}', 2)
        except Exception as e:
            self.debug(f'arg decoding error: {e}', 2)

        if cmd in cdh.commands:
            try:
                if cmd_args:
                    self.debug(f'running {cdh.commands[cmd]} (with args: {cmd_args})')
                    cdh.commands[cmd](self, cmd_args)
                else:
                    self.debug(f'running {cdh.commands[cmd]} (no args)')
                    cdh.commands[cmd](self)
            except Exception as e:
                self.debug(f'something went wrong: {e}')
                await cubesat.radio.send(str(e).encode())
        else:
            self.debug('invalid command!')
            await cubesat.radio.send(b'invalid cmd' + cmd)

    def handle_disk_buffered_message(self, header, response):
        """Handler function for the disk_buffered_message message type"""
        if header == headers.DISK_BUFFERED_START:
            self.try_write('disk_buffered_message', 'wb', response)
        else:
            if response != self.cmsg_last:
                self.try_write('disk_buffered_message', 'ab', response)
            else:
                self.debug('Repeated chunk')

        self.cmsg_last = response
        if header == headers.DISK_BUFFERED_END:
            self.cmsg_last = None

    def try_write(self, file, mode, data):
        """Try to write to the sd card. If it fails, print an error"""
        if not cubesat.sdcard or not cubesat.vfs:
            self.debug('No SD card attached, skipping writing to file')
            return
        try:
            f = open(f"/sd/{file}", mode)
            f.write(data)
            f.close()
            self.debug('Sucesfully wrote to file')
        except Exception as e:
            self.debug(f'Error while writing to file {e}')
