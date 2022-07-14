"""
Python system check script for PyCubed satellite board
PyCubed Mini mainboard-v02 for Pocketqube Mission
Radio Test
* Author(s): Aleksei Seletskiy, Yashika Batra
"""

import pycubed

ANTENNA_ATTACHED = False

send_text = "Hello World! Sending a beacon"
receive_text = "Hello World! Receiving a response"


async def radio_test(cubesat, result_dict, testidx):
    attempts = 5

    if testidx == "Both":
        success = False
        success_count = 0

        print("Transmission and Reception Test: " +
              "Sending Message and Awaiting Groundstation Response (25s)")

        for i in range(attempts):
            # send beacon text and keep listening
            pycubed.send(send_text, keep_listening=True)

            # await a response for 5 seconds
            heard_something = await pycubed.await_rx(timeout=5.0)

            if heard_something:
                # get response
                response = pycubed.receive(keep_listening=True, with_ack=ANTENNA_ATTACHED)
                response_text = str(response, "ascii")

                # if the response is correct, print an acknowledgement
                if response_text == receive_text:
                    success_count += 1
                    success = True
                    print("Attempt", str(i + 1) + ": Received \"" + response_text + "\"")
                else:  # else print an acknowledgement
                    print("Attempt", str(i + 1) + ": Received \"" + response_text +
                          "\", Expected \"" + receive_text + "\"")
            else:  # if no packet received, print an acknowledement
                print("Attempt", str(i + 1) + ": Did not receive \"" + receive_text + "\"")

        return success, success_count, attempts

    if testidx == "Receive":
        receive_success = False
        receive_count = 0

        print("Reception Test: Awaiting Groundstation Message (25s)")
        for i in range(attempts):
            # await a response for 5 seconds
            heard_something = await pycubed.await_rx(timeout=5.0)

            if heard_something:
                # get response
                response = pycubed.receive(keep_listening=True, with_ack=ANTENNA_ATTACHED)
                response_text = str(response, "ascii")

                # if the response is correct, print an acknowledgement
                if response_text == receive_text:
                    receive_count += 1
                    receive_success = True
                    print("Attempt", str(i + 1) + ": Received \"" + response_text + "\"")
                else:  # else print an acknowledgement
                    print("Attempt", str(i + 1) + ": Received \"" + response_text +
                          "\", Expected \"" + receive_text + "\"")
            else:  # if no packet received, print an acknowledement
                print("Attempt", str(i + 1) + ": Did not receive \"" + receive_text + "\"")
        return receive_success, receive_count, attempts

    if testidx == "Send":
        send_success = False
        send_count = 0

        print("Transmission Test: Sending Message to Groundstation (25s)")
        for i in range(attempts):
            # send beacon text and keep listening
            pycubed.send(send_text, keep_listening=True)

            # if the message is sent correctly, print an acknowledgement
            message_sent = input("Does the groundstation confirm correct reception? (Y/N)")
            if message_sent == "Y":
                send_success = True
                send_count += 1
                print("Attempt", str(i + 1) + ": Sent \"" + send_text + "\"")
            else:  # else print an acknowledgement
                print("Attempt", str(i + 1) + ": Did not send \"" + send_text + "\"")

        return send_success, send_count, attempts


def run(cubesat, hardware_dict, result_dict, antenna_attached):
    ANTENNA_ATTACHED = antenna_attached
    # if no Radio detected, update result dictionary and return
    if not hardware_dict['Radio']:
        result_dict['Radio_Receive_Beacon'] = ('Cannot test reception; no Radio detected', False)
        result_dict['Radio_Send_Beacon'] = ('Cannot test sending beacon; no Radio detected', False)
        return result_dict

    # if no antenna detected, update result dictionary and return
    if not ANTENNA_ATTACHED:
        result_dict['Radio_Receive_Beacon'] = ('Cannot test reception; no Antenna attached', False)
        result_dict['Radio_Send_Beacon'] = ('Cannot test sending beacon; no Antenna attached', False)
        return result_dict

    # if Radio and antenna detected, run other tests
    else:
        # test transmission and reception together
        result, count, attempts = radio_test(cubesat, result_dict, "Both")
        result_val_string = ("Succeeded in sending and receiving message" + str(count) +
                             "/" + str(attempts) + " times.")

        # if the test fails
        if not result:
            # individually test reception and update result dict
            receive_result, receive_count, receive_attempts = radio_test(cubesat, result_dict, "Receive")
            receive_val_string = ("Succeeded in receiving message" + str(receive_count) +
                                  "/" + str(receive_attempts) + " times.")
            result_dict['Radio_Receive_Beacon'] = (receive_val_string, receive_result)

            # individually test transmission and update result dict
            send_result, send_count, send_attempts = radio_test(cubesat, result_dict, "Send")
            send_val_string = ("Succeeded in sending message" + str(send_count) +
                               "/" + str(send_attempts) + " times.")
            result_dict['Radio_Send_Beacon'] = (send_val_string, send_result)

        # if the test succeeds
        else:
            # update result_dict
            result_dict['Radio_Receive_Beacon'] = (result_val_string, True)
            result_dict['Radio_Send_Beacon'] = (result_val_string, True)

    return result_dict
