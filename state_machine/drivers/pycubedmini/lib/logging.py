from os import listdir, stat, statvfs, remove, mkdir, rmdir
import time
from lib.pycubed import cubesat

sd_card_directory = "/sd/"
DEFAULT_FOLDER = "debug"
INFO_FILENAME = "loginfo.txt"
MAX_FILE_SIZE = 1E8

sd_buffer = dict()
MAX_BUFFER_SIZE = 1000

# start time in nanoseconds
global start_time
start_time = time.monotonic_ns()
# time_interval = 6 * 10**11 # 10 minutes in nano seconds
# file_name_interval = 60 * 10**9 # 1 minute in nano seconds
time_interval = 5 * 10**9
file_name_interval = 10**9


def read_infotxt(folder=DEFAULT_FOLDER):
    """
    retrieve the logfile number from loginfo.txt
    """

    # placeholder value
    logfile_starttime = 0

    # if loginfo.txt doesn't exist, write it with logfile_starttime 0 and read
    if INFO_FILENAME not in listdir(f"{sd_card_directory}/{folder}"):
        write_infotxt(logfile_starttime, folder)
        return logfile_starttime

    # if loginfo.txt does exist, read the existing loginfo.txt
    if INFO_FILENAME in listdir(f"{sd_card_directory}/{folder}"):
        # read the contents and retrieve logfile_starttime
        info_filename_dir = f"{sd_card_directory}/{folder}/{INFO_FILENAME}"
        info_file = open(info_filename_dir, "r")
        info_file_contents = info_file.read()
        info_file_lines = info_file_contents.split("\n")
        # get logfile_starttime
        logfile_starttime = int(info_file_lines[2])
        # close the file
        info_file.close()

    # return logfile_starttime read from info.txt
    return logfile_starttime


def write_infotxt(logfile_starttime, folder=DEFAULT_FOLDER):
    """
    write loginfo.txt in a certain format based on logfile_starttime
    """

    # overwrite the current info file
    info_filename_dir = f"{sd_card_directory}/{folder}/{INFO_FILENAME}"
    info_file = open(info_filename_dir, "w")

    # write a timestamp, the current logfile_starttime
    info_file.write(f"{time.monotonic()}\n")  # line 0
    info_file.write("logfile_start_time:\n")      # line 1
    info_file.write(f"{logfile_starttime}\n")     # line 2

    # close file
    info_file.close()


def get_logfile_name_dir(logfile_starttime, folder=DEFAULT_FOLDER):
    logfile_name = get_logfile_name(logfile_starttime, folder)
    return f"{sd_card_directory}/{folder}/logs/{logfile_name}"


def get_logfile_name(logfile_starttime, folder):
    """
    format the logfile_name based on logfile_starttime and return
    """
    logfile_endtime = (logfile_starttime + time_interval) // (10**9)
    bootcount = cubesat.get_boot_count()
    return (f"{folder}_log_reboot{bootcount:03}" +
            f"_start{logfile_starttime:06}_end{logfile_endtime:06}.txt")


def new_log(logfile_starttime, folder=DEFAULT_FOLDER):
    """
    Create a new log file
    Write a header and return the new logfile_starttime
    """

    # After you fill up 1000 files (~ 1 GB), overwrite old files
    logfile_starttime = start_time // (10**9)
    logfile_name = get_logfile_name(logfile_starttime)
    logfile_name_dir = get_logfile_name_dir(logfile_starttime, folder)

    # if logfile_name doesn't exist, create it
    if logfile_name not in listdir(f"{sd_card_directory}/{folder}/logs/"):
        # create logfile and write a header
        logfile = open(logfile_name_dir, "x")
        logfile.write(f"########## Created: {time.monotonic()} ##########\n")
        logfile.close()
    # if logfile_name exists, overwrite
    else:
        # overwrite existing logfile and write a header
        logfile = open(logfile_name_dir, "w")
        logfile.write(f"########## Created: {time.monotonic()} ##########\n")
        logfile.close()

    # print a confirmation message that a new logfile was created
    write_infotxt(logfile_starttime, folder)

    return logfile_starttime


def buffered_log(msg, max_file_size=MAX_FILE_SIZE, folder=DEFAULT_FOLDER,
                 max_buffer_size=MAX_BUFFER_SIZE):
    """
    Add msg content to the correct buffer
    If the buffer is full, write it to the correct folder
    """
    # add the message to the buffer for the given folder
    if folder in sd_buffer:
        sd_buffer[folder] += msg
    else:
        sd_buffer[folder] = msg

    # if the buffer is full, log
    if len(sd_buffer[folder]) > max_buffer_size:
        # get msg from buffer
        msg = sd_buffer[folder]
        # write to file
        unbuffered_log(msg=msg, max_file_size=max_file_size, folder=folder)
        # update buffer
        sd_buffer[folder] = ""


def unbuffered_log(msg, max_file_size=MAX_FILE_SIZE, folder=DEFAULT_FOLDER):
    """
    Write msg content to the correct folder
    """
    global start_time
    current_time = time.monotonic_ns()
    delta_time = current_time - start_time
    write_new_file = delta_time > time_interval
    if write_new_file:
        start_time = current_time

    if cubesat.sdcard:
        # if hardware logs folder missing, create folder and loginfo.txt
        if folder not in listdir(sd_card_directory):
            # create given hardware logs folder
            mkdir(f"{sd_card_directory}/{folder}/")
            # create loginfo.txt
            logfile_starttime = 0
            write_infotxt(logfile_starttime, folder)

        # get the current logfile_starttime for the given folder
        logfile_starttime = read_infotxt(folder)
        # get current logfile_name and logfile_name_dir
        logfile_name_dir = get_logfile_name_dir(logfile_starttime, folder)

        # if the logs directory is missing, create logs directory and first log
        if "logs" not in listdir(f"{sd_card_directory}/{folder}"):
            # create logs directory
            mkdir(f"{sd_card_directory}/{folder}/logs/")
            # create first logfile
            logfile = open(logfile_name_dir, "x")
            logfile.write(
                f"########## Created: {time.monotonic()} ##########\n")
            logfile.close()

        # if it's been more than some given time interval
        if write_new_file:
            print(f"it's been {time_interval} ns, writing a new file")
            # create a new logfile
            logfile_starttime = new_log(logfile_starttime)
            # get the logfile_name_dir again based on new logfile_starttime
            logfile_name_dir = get_logfile_name_dir(logfile_starttime, folder)

        # open the current logfile and write message msg
        with open(logfile_name_dir, "a+") as logfile:
            logfile.write(msg)


def log(msg, max_file_size=MAX_FILE_SIZE, folder=DEFAULT_FOLDER, buffer=False,
        max_buffer_size=MAX_BUFFER_SIZE):
    """
    Handle buffered vs. unbuffered logs
    User-side
    """

    # if we are writing to debug, unbuffer it by default
    if folder == DEFAULT_FOLDER:
        unbuffered_log(msg=msg, max_file_size=max_file_size, folder=folder)

    # if we are not writing to debug, check if we're using the buffer or not
    else:
        # if we are doing a buffered log
        if buffer:
            # add to buffer for folder
            buffered_log(msg=msg, folder=folder,
                         max_buffer_size=max_buffer_size)
        # if we are not doing a buffered log
        else:
            unbuffered_log(msg=msg, max_file_size=max_file_size, folder=folder)


def get_buffer():
    return sd_buffer


def storage_stats():
    """
    return the storage statistics about the SD card and
    mainboard file system
    """
    sd_usage = None
    # if cubesat sd card is not None
    if cubesat.sdcard:
        # statvfs returns info about SD card (mounted file system)
        sd_storage_stats = statvfs(sd_card_directory)
        sd_storage_used = sd_storage_stats[3]
        sd_storage_total = sd_storage_stats[2]
        sd_usage = sd_storage_used / sd_storage_total

    # returns information about the overall file system
    fs_storage_stats = statvfs('/')
    fs_storage_used = fs_storage_stats[3]
    fs_storage_total = fs_storage_stats[2]
    fs_usage = fs_storage_used / fs_storage_total

    # return both sets of information
    return (fs_usage, sd_usage)


def clear_storage(folder):
    """
    Clear the logs directory and info.txt file on the sd card's given folder
    """
    # get the filepath for the info file for the given folder
    info_filename_dir = f"{sd_card_directory}/{folder}/{INFO_FILENAME}"

    # if a logs directory exists in the given folder
    if "logs" in listdir(f"{sd_card_directory}/{folder}"):
        # remove all logfiles in the logs directory
        for logfile in listdir(f"{sd_card_directory}/{folder}/logs/"):
            remove(f"{sd_card_directory}/{folder}/logs/{logfile}")
        # remove the logs directory
        rmdir(f"{sd_card_directory}/{folder}/logs")

    # remove the info file from the given folder
    if INFO_FILENAME in listdir(f"{sd_card_directory}/{folder}"):
        remove(info_filename_dir)

    rmdir(f"{sd_card_directory}/{folder}")


def clear_all_storage():
    """
    Clear the all files and directories on the sd card
    """

    # for all files and folders in the sd directory
    for file_or_folder in listdir(sd_card_directory):
        # get the stat info for the given file or folder
        file_or_folder_stat = stat(f"{sd_card_directory}/{file_or_folder}")
        # if the folder is a directory, clear the folder
        if file_or_folder_stat[0] == 16384:
            folder = file_or_folder
            clear_storage(folder)
        # else, the folder is a file, remove the file
        else:
            sdfile = file_or_folder
            remove(f"/sd/{sdfile}")
