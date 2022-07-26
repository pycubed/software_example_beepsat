"""
Python system check script for PyCubed satellite board
PyCubed Mini mainboard-v02 for Pocketqube Mission
SD Card Logging Test
* Author(s): Yashika Batra
"""

import os


def sd_test():
    """
    Run a basic test; create a file and test existence, write to and
    read from a file, delete file and test existence. Return result_dict
    values accordingly
    """

    # create filepaths
    fp = "test.txt"
    test_fp = "/sd/" + fp

    # try to create a file with the test filepath
    try:
        test_file = open(test_fp, "x")
    except OSError:
        # if the file already exists, remove it and create a new file
        os.remove(test_fp)
        test_file = open(test_fp, "x")

    print("Directory after test.txt was created: ", os.listdir("/sd/"))
    if fp not in os.listdir("/sd/"):
        return ("File creation failed. ", False)

    # write to file
    test_string = "Hello World! This is a test file.\n"
    try:
        test_file.write(test_string)
    except OSError as e:
        print("Unable to write to file. " + str(e))
        return ("Unable to write to file. " + str(e), False)
    test_file.close()

    # read from file
    try:
        test_file_read = open(test_fp, "r")
        test_string_read = test_file_read.read()
    except OSError as e:
        print("Unable to read from file. " + str(e))
        return ("Unable to read from file. " + str(e), False)

    if test_string_read != test_string:
        print("File not written to or read from correctly.")
        return ("File not written to or read from correctly.", False)

    # delete file
    os.remove(test_fp)
    print("Directory after test.txt was removed: ", os.listdir("/sd/"))

    if fp in os.listdir("/sd/"):
        return ("File deletion failed. ", False)

    # if nothing has failed so far, return success
    return ("SD Card passed all tests: Created, wrote to, " +
            "read from, and deleted a file successfully.", True)


def run(hardware_dict, result_dict):
    """
    Check that the correct hardware is initialized and run tests
    """

    # if no SD Card detected, update result dictionary and return
    if not hardware_dict['SDcard']:
        result_dict['SDcard_Logging'] = (
            'Cannot test logging; no SD Card detected', False)
        return result_dict

    # if SD Card detected, run other tests
    print("Starting logging test...")
    result_val_string, result_val_bool = sd_test()
    result_dict['SDcard_Logging'] = (result_val_string, result_val_bool)
    print("Logging test complete.")
    print("")

    return result_dict
