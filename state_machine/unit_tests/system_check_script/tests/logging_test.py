"""
Python system check script for PyCubed satellite board
PyCubed Mini mainboard-v02 for Pocketqube Mission
SD Card Logging Test
* Author(s): Yashika Batra
"""

def run(cubesat, hardware_dict, result_dict):
    # if no SD Card detected, update result dictionary and return
    if not hardware_dict['SDcard']:
        result_dict['SD_Card_Logging'] = ('Cannot test logging; no SD Card detected', False)
        return result_dict

    # if SD Card detected, run other tests
    return result_dict
