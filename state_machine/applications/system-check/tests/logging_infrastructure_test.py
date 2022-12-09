"""
System check module for PyCubed Mini satellite
Logging Infrastructure Test
"""

from os import listdir
from lib.pycubed import cubesat
import time

sd_card_directory = "/sd/"

time_interval = 5 * 10 ** 9
file_name_interval = 10 ** 9
max_buffer_size = 200


async def run(result_dict):
    """
    If the SD card has been properly initialized, log 1800 characters
    100 characters at a time, with a max buffer size of 200 characters.
    Make sure that 2 files have been created as a result of these logs.
    """

    cubesat.logger.time_interval = 5 * 1 ** 9  # five seconds
    cubesat.logger.file_name_interval = 10 ** 9  # one second
    cubesat.logger.max_buffer_size = 200

    if not cubesat.sdcard:
        print("Cannot test Logging Infrastructure; no SD Card detected")
        result_dict["LoggingInfrastructure_Test"] = (
            "Cannot test Logging Infrastructure; no SD Card detected", None)

    print("Starting logging infrastructure test...")

    print(f"Initial, /sd/: {listdir(sd_card_directory)}")
    cubesat.clear_logs()
    print(f"After clearing storage, /sd/: {listdir(sd_card_directory)}")

    # buffered write; testing this tests unbuffered writes by default
    print("Testing buffered and unbuffered writes...")
    # for each folder in the folders array
    sd_buffer = cubesat.logger.get_buffer()
    buffer_working = True
    num_folders = 2
    folders = []
    folders_written = [True] * num_folders

    for i in range(num_folders):
        folders.append(f"folder{i}")

    # length = 40 characters
    msg1 = f"Testing buffered write! Folder: {folders[0]}\n"
    msg2 = f"Testing buffered write! Folder: {folders[1]}\n"
    msgs = [msg1, msg2]

    for i in range(num_folders):
        filenum = 0
        buffer_written = 0
        max_buffer_size = 200
        msg = msgs[i] * 10

        # write 2 files worth of messages (sleep 5 seconds between writes)
        while filenum < 2:
            # write buffered logs
            cubesat.log(msg, folder=folders[i], buffer=True)

            # if buffer is empty, increment count
            if sd_buffer[folders[i]] == "":
                buffer_written += 1

            # increment number of files written
            filenum += 1

            # sleep (waiting for the next file's creation)
            time.sleep(5)

        # check if the buffer was emptied out the correct number of times
        buffer_working = (buffer_working and
                          buffer_written >= len(msg) // max_buffer_size - 1)

    for i in range(num_folders):
        # check if folderi has all the correct logfiles
        if folders[i] in listdir(f"{sd_card_directory}logs"):
            for f in listdir(f"{sd_card_directory}logs/{folders[i]}"):
                f_reader = open(
                    f"{sd_card_directory}logs/{folders[i]}/{f}", "r")
                folderfile_string = f_reader.read()
                if (msgs[i] not in folderfile_string or
                        len(listdir(f"{sd_card_directory}logs/{folders[i]}")) < 2):
                    folders_written[i] = False
        else:
            print(f"Folder{i} not created.")
            folders_written[i] = False

    if buffer_working:
        print("Buffer is correctly updated.")
    else:
        print("Buffer is not correctly updated.")

    for i in range(num_folders):
        if folders_written[i]:
            print(f"Folder{i} has the correct message written to its files.")
        else:
            print(f"Folder{i}'s files do not contain the correct message.")

    print("Testing unbuffered vs. buffered writes is complete.")
    print(f"/sd/ directory: {listdir(sd_card_directory)}")
    for folder in listdir(f"{sd_card_directory}logs/"):
        if folder in folders:
            folder_logs_contents = listdir(f'{sd_card_directory}logs/{folder}')
            print(f"logs in /sd/logs/{folder} directory: {folder_logs_contents}")

    if folders_written == [True] * len(folders_written):
        result_string = ("All folders have been written to correctly." +
                         " Please perform any necessary manual checks.")
    else:
        result_string = ("Some folder was not written to correctly." +
                         " Please check above messages to troubleshoot.")
    print(result_string)
    result_dict["LoggingInfrastructure_Test"] = (
        result_string, folders_written == [True] * len(folders_written))

    print(f"Ending, /sd/: {listdir(sd_card_directory)}")
    cubesat.clear_logs()
    print(f"After Clearing Storage, /sd/: {listdir(sd_card_directory)}")
    print("Logging Infrastructure Test complete.\n")
