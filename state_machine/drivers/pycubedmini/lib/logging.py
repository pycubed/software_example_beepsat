from os import listdir, stat, statvfs, remove, mkdir, rmdir
import time
import lib.pycubed as cubesat
import digitalio, microcontroller
import storage

info_filename = "info.txt"
info_filename_dir = f"/sd/info.txt"
max_file_size = 1E8

def read_infotxt():
    """ 
    retrieve the logfile number from info.txt 
    """

    # placeholder value
    logfile_count = 0

    # if info.txt doesn't exist, write it with logfile_count 0 and read
    if info_filename not in listdir("/sd"):
        write_infotxt(0)
        return read_infotxt()

    # if info.txt does exist, read the existing info.txt
    if info_filename in listdir("/sd/"):
        # read the contents and retrieve logfile_count
        info_file = open(info_filename_dir, "r")
        info_file_contents = info_file.read()
        info_file_lines = info_file_contents.split("\r\n")
        # get logfile_count
        logfile_count = int(info_file_lines[2])
        # close the file
        info_file.close()
    
    # return logfile_count read from info.txt
    return logfile_count


def write_infotxt(logfile_count):
    """ 
    write info.txt in a certain format based on logfile_count
    """

    # overwrite the current info file
    info_file = open(info_filename_dir, "w")
    # write a timestamp, the current logfolder_count, and the current logfolder_arr
    info_file.write(f"{time.monotonic()}\r\n")  # line 0
    info_file.write(f"logfile_count:\r\n")      # line 1
    info_file.write(f"{logfile_count}\r\n")     # line 2
    # close file
    info_file.close()


def rjust(string, length, char):
    """
    python string builtin rjust doesn't exist in circuitpython
    redefining this function to make filename formatting easier
    """
    string_length = len(string)
    if string_length < length:
        padding = char * (length - string_length)
        return f"{padding}{string}"

    if string_length == length:
        return string
    
    if string_length > length:
        return string[0:length]


def get_logfile_name_dir(logfile_count):
    logfile_name = get_logfile_name(logfile_count)
    return f"/sd/logs/{logfile_name}"


def get_logfile_name(logfile_count):
    """
    format the logfile_name based on logfile_count and return
    """

    logfile_count_string = rjust(str(logfile_count), 3, '0')
    return f"log{logfile_count_string}.txt"


def new_log(logfile_count):
    """
    Create a new log file
    Retrieve logfolder and logfile numbers from info.txt
    If necessary, create a new logfolder
    Create a new logfile
    Write a header and return logfile path
    """

    # After you fill up 1000 files (~ 1 GB), overwrite old files
    logfile_count += 1
    logfile_count %= 1000
    logfile_name = get_logfile_name(logfile_count)
    logfile_name_dir = get_logfile_name_dir(logfile_count)

    # if logfile_name doesn't exist, create it
    if logfile_name not in listdir("/sd/logs/"):
        # create logfile and write a header
        logfile = open(logfile_name_dir, "x")
        logfile.write(f"########## Created: {time.monotonic()} ##########\r\n")
        logfile.close()
    # if logfile_name exists, overwrite
    else:
        # overwrite existing logfile and write a header
        logfile = open(logfile_name_dir, "w")
        logfile.write(f"########## Created: {time.monotonic()} ##########\r\n")
        logfile.close()

    # print a confirmation message that a new logfile was created
    write_infotxt(logfile_count)

    return logfile_count


def log(msg, max_file_size=max_file_size):
    """
    Create/open file and write logs
    max_file_size is a default value, set to 1E8 at the top of the file

    TODO: find a way to identify the first and last packets of a long log
    (if we haven't already)
    - write a timestamp before the first packet
    - write "\r\n" after the last packet
    """

    # get current logfile_arr, logfile_count from info.txt
    logfile_count = read_infotxt()  # if info.txt doesn't exist, write with 0
    # get current logfile_name and logfile_name_dir
    logfile_name_dir = get_logfile_name_dir(logfile_count)

    # if the logs directory is missing, create logs directory and first log file
    if "logs" not in listdir("/sd/"):
        # create logs directory
        mkdir("/sd/logs/")
        # create first logfile
        logfile = open(logfile_name_dir, "x")
        logfile.write(f"########## Created: {time.monotonic()} ##########\r\n")
        logfile.close()

    # if file length + message length is greater than 1MB (1E8)
    if stat(logfile_name_dir)[6] + len(msg) > max_file_size:
        # create a new logfile
        logfile_count = new_log(logfile_count)
        # get the logfile_name_dir again based on new logfile_count
        logfile_name_dir = get_logfile_name_dir(logfile_count)

    # open the current logfile and write message msg
    if cubesat.sd:  # if the SD card is initialized
        with open(logfile_name_dir, "a+") as file:
            file.write(f"{msg}")


def storage_stats():
    """
    return the storage statistics about the SD card and
    mainboard file system
    """
    sd_storage_percent = 0
    # if cubesat sd card is not None
    if cubesat.sd:
        # statvfs returns info about SD card (mounted file system)
        sd_storage_stats = statvfs('/sd/')
        sd_storage_used = sd_storage_stats[3]
        sd_storage_total = sd_storage_stats[2]
        sd_storage_percent = int(100 * sd_storage_used / sd_storage_total)

    # returns information about the overall file system
    fs_storage_stats = statvfs('/')
    fs_storage_used = fs_storage_stats[3]
    fs_storage_total = fs_storage_stats[2]
    fs_storage_percent = int(100 * fs_storage_used / fs_storage_total)

    # return both sets of information
    return (fs_storage_percent, sd_storage_percent)


def clear_storage():
    """
    Clear the logs directory and info.txt file on the sd card
    """
    if "logs" in listdir("/sd"):
        for logfile in listdir("/sd/logs/"):
            # to test: print(open(f"/sd/logs/{logfile}", "r").read())
            remove(f"/sd/logs/{logfile}")
        rmdir("/sd/logs")
    if info_filename in listdir("/sd"):
        remove(info_filename_dir)
