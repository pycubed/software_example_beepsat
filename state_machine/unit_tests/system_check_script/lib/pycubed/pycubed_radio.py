"""
CircuitPython driver for PyCubed satellite board radio
PyCubed Mini mainboard-v02 for Pocketqube Mission
* Author(s): Max Holliday, Yashika Batra
"""
from pycubed import pocketqube as cubesat
from pycubed_logging import log
from os import stat


if cubesat.hardware['Radio']:
    def send(data,
             *,
             keep_listening=False,
             destination=None,
             node=None,
             identifier=None,
             flags=None):
        cubesat.radio.send(
            data,
            keep_listening=keep_listening,
            destination=destination,
            node=node,
            identifier=identifier,
            flags=flags)
        return 0

    def listen():
        cubesat.radio.listen()

    def receive(*,
                keep_listening=True,
                with_header=False,
                with_ack=False,
                timeout=None,
                debug=False):
        cubesat.radio.receive(
            keep_listening=keep_listening,
            with_header=with_header,
            with_ack=with_ack,
            timeout=timeout,
            debug=debug
        )

    def sleep():
        cubesat.radio.sleep()

    def create_packets(c_size, send_buffer, filename):
        """
        send a file given packet size, buffer size, and the filename
        """

        # number of packets is the size of the file / packet size
        num_packets = int(stat(filename)[6] / c_size)

        # open the file
        with open(filename, "rb") as f:
            # for each packet
            for i in range(num_packets + 1):
                # move the cursor to the end of i * packet size,
                # add to buffer
                f.seek(i * c_size)
                f.readinto(send_buffer)

                # return bytes; yield keyword returns without destroying
                # states of local vars
                yield bytes([i, 0x45, num_packets])

    def send_file(filename):
        # define some base case c_size and send_buffer
        c_size = 1
        send_buffer = bytearray()

        for packet in create_packets(c_size, send_buffer, filename):
            send(packet)

else:
    # log that radio was accessed without being initialized
    log("Radio accessed without being initialized")
