from lib.logging import get_logfile_name, clear_storage, log
from os import listdir


def run(hardware_dict, result_dict):
    """
    If the SD card has been properly initialized, log 1800 characters
    100 characters at a time, with a max file size of 1000 characters.
    Make sure that 2 files have been created as a result of these logs.
    """

    if not hardware_dict["SDcard"]:
        result_dict["LoggingInfrastructure_Test"] = (
            "Cannot test Logging Infrastructure; no SD Card detected", None)
        return result_dict

    print("Starting logging infrastructure test...")
    clear_storage()
    print(f"/sd/ directory: {listdir('/sd/')}")

    # log 1800 characters
    for i in range(18):
        msg = 'x' * 100
        log(msg, 1000)

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

    clear_storage()
