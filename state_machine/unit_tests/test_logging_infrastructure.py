import sys

sys.path.insert(0, './state_machine/drivers/pycubedmini/lib')

from logging import get_logfile_name, clear_storage, log
from os import listdir

def test():
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
        print("""Log and new log functions are working;
files were created successfully.""")
    else:
        print("New log function not working.")


clear_storage()
test()
clear_storage()
