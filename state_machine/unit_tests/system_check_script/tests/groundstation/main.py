"""
Python system check script for PyCubed satellite board
PyCubed Mini mainboard-v02 for Pocketqube Mission
Radio Groundstation Test
* Author(s): Aleksei Seletskiy, Yashika Batra
"""

import board
import busio
import digitalio
from lib import adafruit_rfm9x
import time

RADIO_FREQ_MHZ = 433.0  # Frequency of the radio in Mhz.

# Define pins connected to the chip, use these if wiring up the breakout according to the guide:
CS = digitalio.DigitalInOut(board.D5)
RESET = digitalio.DigitalInOut(board.D6)

# Initialize SPI bus.
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Initialze RFM radio
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)
# word, encryption, frequency deviation, or other settings!

# You can however adjust the transmit power (in dB).  The default is 13 dB but
# high power radios like the RFM95 can go up to 23 dB:
rfm9x.tx_power = 13


def run():
    attempts = 5
    receive_text = "Hello World! Sending a beacon"
    send_text = "Hello World! Receiving a response"

    testidx = input("Please enter what test you would like to run.\n" +
                    "If testing satellite reception, enter \"Receive\"\n" +
                    "If testing satellite transmission, enter \"Send\"\n" +
                    "If testing both, enter \"Both\": ")

    # if testing satellite transmission, attempt to receive a message
    if testidx == "Send":
        receive_success = False
        receive_count = 0

        print("Awaiting Satellite Beacon (25s)")
        for i in range(attempts):
            packet = rfm9x.receive(timeout=5.0)

            # if a packet is received
            if packet is not None:
                # convert packet to ascii
                packet_text = str(packet, "ascii")

                # if correct message, send response
                if packet_text == receive_text:
                    receive_count += 1
                    receive_success = True
                    print("Attempt", str(i + 1) + ": Received \"" + packet_text + "\"")
                else:  # if incorrect message, print acknowledgement
                    print("Attempt", str(i + 1) + ": Received \"" + packet_text +
                          "\", Expected \"" + receive_text + "\"")
            # if nothing received, print acknowledgement
            else:
                print("Attempt", str(i + 1) + ": Did not receive \"" + receive_text + "\"")

        # print stats and return success boolean
        print("Succeeded in sending and receiving message" + str(receive_count) +
              "/" + str(attempts) + " times.")
        return receive_success

    # if testing satellite reception, attempt to send a message
    if testidx == "Send":
        print("Sending Message to Satellite (25s)")
        # send a response 5 times and wait 5 seconds each time
        for i in range(attempts):
            # print acknowledgement that a message was sent
            rfm9x.send(send_text)
            print("Attempt", str(i + 1) + ": Sending \"" + send_text + "\"")
            time.sleep(5)
        # print acknowledgement that x attempts were made
        print("Sent message" + str(attempts) + " times.")
        return True

    # if testing both reception and transmission,
    # attempt to receive a message and send response
    if testidx == "Both":
        success = False
        success_count = 0

        print("Awaiting Satellite Beacon (25s)")
        for i in range(attempts):
            packet = rfm9x.receive(timeout=5.0)

            # if a packet is received
            if packet is not None:
                # convert packet to ascii
                packet_text = str(packet, "ascii")

                # if correct message, send response and print acknowledgement
                if packet_text == receive_text:
                    success_count += 1
                    success = True
                    rfm9x.send(send_text)
                    print("Attempt", str(i + 1) + ": Received \"" + packet_text +
                          "\". Sending \"" + send_text + "\" in response.")
                else:  # if incorrect message, print acknowledgement
                    print("Attempt", str(i + 1) + ": Received \"" + packet_text +
                          "\", Expected \"" + receive_text + "\"")
            # if nothing received, print acknowledgement
            else:
                print("Attempt", str(i + 1) + ": Did not receive \"" + receive_text + "\"")

        # print stats and return success boolean
        print("Succeeded in sending and receiving message" + str(success_count) +
              "/" + str(attempts) + " times.")
        return success


run()
print("Groundstation Test Complete.")
