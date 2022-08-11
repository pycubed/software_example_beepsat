from lib.logging import get_logfile_name, clear_storage, log
from os import listdir


def run(hardware_dict, result_dict):
    """
    check that the SD Card is initialized and test the logging infrastructure
    log multiple files' worth of content, and check that the correct filenames
    and correct number of files were created
    """

    # check that the SD card is initialized
    if not hardware_dict["SDcard"]:
        result_dict["LoggingInfrastructure_Test"] = (
            "Cannot test Logging Infrastructure; no SD Card detected", None)
        return result_dict

    print("Starting logging infrastructure test...")
    clear_storage()
    print(f"/sd/ directory: {listdir('/sd/')}")

    # log 1900 characters
    for i in range(18):
        msg = 'x' * 100
        log(msg, 1000)

    # check that log000.txt and log001.txt were created
    logfile1 = get_logfile_name(0)
    logfile2 = get_logfile_name(1)
    logfile1_created = logfile1 in listdir("/sd/logs/")
    logfile2_created = logfile2 in listdir("/sd/logs/")

    print(f"/sd/ directory: {listdir('/sd/')}")
    print(f"/sd/logs/ directory: {listdir('/sd/logs/')}")

    # update result dictionary
    if logfile1_created and logfile2_created:
        result_string = """Log and new log functions are working;
files were created successfully."""
        result_dict["LoggingInfrastructure_Test"] = (result_string, True)
        print(result_string)
    else:
        result_string = "New log function not working."
        result_dict["LoggingInfrastructure_Test"] = (result_string, False)
        print(result_string)

    print("Logging Infrastructure Test complete.\n")
    clear_storage()
