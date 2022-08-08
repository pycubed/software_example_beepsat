from lib.logging import get_logfile_name, clear_storage, log
from os import listdir


def run(hardware_dict, result_dict):

    # if no SD Card detected, update result dictionary and return
    if not hardware_dict["SDcard"]:
        result_dict["LoggingInfrastructure_Test"] = (
            "Cannot test Logging Infrastructure; no SD Card detected", None)
        return result_dict

    # else, clear storage and run test
    print("Starting logging infrasturcure test...")
    clear_storage()
    print(f"/sd/ directory: {listdir('/sd/')}")

    for i in range(18):
        msg = 'x' * 100
        log(msg, 1000)

    logfile1 = get_logfile_name(0)
    logfile2 = get_logfile_name(1)

    # should create 2 files
    logfile1_created = logfile1 in listdir("/sd/logs/")
    logfile2_created = logfile2 in listdir("/sd/logs/")

    print(f"/sd/ directory: {listdir('/sd/')}")
    print(f"/sd/logs/ directory: {listdir('/sd/logs/')}")

    if logfile1_created and logfile2_created:
        result_string = """Log and new log functions are working;
files were created successfully."""
        result_dict["LoggingInfrastructure_Test"] = (result_string, True)
        print(result_string)
    else:
        result_string = "New log function not working."
        result_dict["LoggingInfrastructure_Test"] = (result_string, False)
        print(result_string)
    
    print("Logging Infrasturcure Test complete.\n")

    clear_storage()
