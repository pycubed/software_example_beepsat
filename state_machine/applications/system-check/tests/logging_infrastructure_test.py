from lib.logging import *
from os import listdir
from lib.pycubed import cubesat


def run(result_dict):
    """
    If the SD card has been properly initialized, log 1800 characters
    100 characters at a time, with a max file size of 1000 characters.
    Make sure that 2 files have been created as a result of these logs.
    """

    if not cubesat.sdcard:
        result_dict["LoggingInfrastructure_Test"] = (
            "Cannot test Logging Infrastructure; no SD Card detected", None)
        return result_dict

    print("Starting logging infrastructure test...")
    clear_all_storage()
    print(f"/sd/ directory: {listdir('/sd/')}")

    folders = ["folder1", "folder2"]
    filenames = []

    # unbuffered write
    # log 1800 characters
    print("Starting an unbuffered write:\n")
    for i in range(18):
        msg = 'x' * 100
        log(msg, max_file_size=1000, buffer=False)
    
    for f in folders:
        # log 1800 characters
        for i in range(18):
            msg = 'x' * 100
            log(msg, max_file_size=1000, folder=f, buffer=False)
    
    # buffered write
    # log 1800 characters
    print("Starting a buffered write:\n")
    for i in range(18):
        msg = 'x' * 100
        log(msg, max_file_size=1000, buffer=True)
    
    for f in folders:
        # log 1800 characters
        for i in range(18):
            msg = 'x' * 10
            log(msg, max_file_size=1000, folder=f, buffer=True)

    logfile1 = get_logfile_name(0)
    logfile2 = get_logfile_name(1)

    print(f"/sd/ directory: {listdir('/sd/')}")
    print(f"/sd/logs/ directory: {listdir('/sd/logs/')}")

    # check that 2 files are created
    logfile1_created = logfile1 in listdir("/sd/logs/")
    logfile2_created = logfile2 in listdir("/sd/logs/")
    if logfile1_created and logfile2_created:
        result_string = """Log and new log functions are working;
files were created successfully."""
    else:
        result_string = "New log function not working."

    print(result_string)
    result_dict["LoggingInfrastructure_Test"] = (
        result_string, logfile1_created and logfile2_created)
    print("Logging Infrastructure Test complete.\n")

    clear_all_storage()
