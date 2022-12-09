from os import listdir, stat, statvfs, remove, mkdir, rmdir
import time

TIME_INTERVAL = 6 * 10 ** 11  # 10 minutes in nano seconds
FILE_NAME_INTERVAL = 60 * 10 ** 9  # 1 minute in nano seconds
MAX_BUFFER_SIZE = 100
SD_DIR = "/sd/"
DEFAULT_FOLDER = "debug"


class Logger():
    def __init__(self, cubesat,
                 time_interval=TIME_INTERVAL,
                 file_name_interval=FILE_NAME_INTERVAL,
                 max_buffer_size=MAX_BUFFER_SIZE,
                 default_folder=DEFAULT_FOLDER):

        self.cubesat = cubesat

        self.start_time = cubesat.BOOTTIME  # start time in nanoseconds
        self.reboot_num = cubesat.c_boot

        self.time_interval = time_interval  # 10 minutes in nano seconds
        self.file_name_interval = file_name_interval  # 1 minute in nano seconds
        self.max_buffer_size = max_buffer_size
        self.default_folder = default_folder

        self.sd_buffer = dict()
        self.MAX_BUFFER_SIZE = 1000

        self.logfile_start_time = self.start_time

    def get_logfile_name_dir(self, folder=DEFAULT_FOLDER):
        logfile_name = self.get_logfile_name(folder)
        return f"{SD_DIR}logs/{folder}/{logfile_name}"

    def get_logfile_name(self, folder):
        """
        format the logfile_name based on logfile_starttime and return
        """
        logfile_endtime = (self.logfile_start_time +
                           (self.time_interval // self.file_name_interval))
        return (f"{folder}_reboot{self.reboot_num:06}" +
                f"_start{self.logfile_start_time:06}_end{logfile_endtime:06}.txt")

    def new_log(self, msg, folder=DEFAULT_FOLDER):
        """
        Create a new log file
        Write a header and return the new logfile_starttime
        """

        # Create new logs whenever we have finished a time interval
        logfile_name = self.get_logfile_name(folder=folder)
        logfile_name_dir = self.get_logfile_name_dir(folder)

        # if logfile_name doesn't exist, create it
        if logfile_name not in listdir(f"{SD_DIR}logs/{folder}"):
            # create logfile and write a header
            logfile = open(logfile_name_dir, "x")
            logfile.write(f"########## Created: {time.monotonic()} ##########\n")
            logfile.write(msg)
            logfile.close()

    def unbuffered_log(self, msg, folder=DEFAULT_FOLDER):
        """
        Write msg content to the correct folder
        """
        # calculate time interval info
        current_time = time.monotonic_ns()
        delta_time = current_time - self.logfile_start_time

        # if it's the first log
        if [] == listdir(f"{SD_DIR}logs/{folder}"):
            # create a new logfile
            self.new_log(msg, folder=folder)
        # else if it's been more than some given time interval
        elif delta_time > self.time_interval:
            # update logfile start time
            self.logfile_start_time = current_time
            self.logfile_start_time //= self.file_name_interval
            # create a new logfile
            self.new_log(msg, folder=folder)
        # else
        else:
            # update logfile_name_dir
            logfile_name_dir = self.get_logfile_name_dir(folder)
            # open the current logfile and write message msg
            with open(logfile_name_dir, "a+") as logfile:
                logfile.write(msg)

    def buffered_log(self, msg, folder=DEFAULT_FOLDER):
        """
        Add msg content to the correct buffer
        If the buffer is full, write it to the correct folder
        """
        # add the message to the buffer for the given folder
        if folder in self.sd_buffer:
            self.sd_buffer[folder] += msg
        else:
            self.sd_buffer[folder] = msg

        # if the buffer is full, log
        if len(self.sd_buffer[folder]) > self.max_buffer_size:
            # get msg from buffer
            msg = self.sd_buffer[folder]
            # write to file
            self.unbuffered_log(msg=msg, folder=folder)
            # update buffer
            self.sd_buffer[folder] = ""

    def create_hardware_folder(self, folder):
        if self.cubesat.sdcard:
            # create folder
            mkdir(f"{SD_DIR}logs/{folder}/")

    def create_logs_folder(self):
        """
        Create the logs folder when we first begin logging
        """
        # if this is the first log ever
        if self.cubesat.sdcard:
            # create log folder
            mkdir(f"{SD_DIR}logs/")

    def log(self, msg,
            folder=DEFAULT_FOLDER,
            buffer=False):
        """
        Handle buffered vs. unbuffered logs
        User-side
        """

        # if this is the first log ever, create logs folder
        if "logs" not in listdir(SD_DIR):
            self.create_logs_folder()

        # if this is the first log to the given folder, create the folder
        if folder not in listdir(f"{SD_DIR}logs/"):
            self.create_hardware_folder(folder)

        # if we are writing to debug, unbuffer it by default
        if folder == self.default_folder:
            self.unbuffered_log(msg=msg, folder=folder)

        # if we are not writing to debug, check if we're using the buffer or not
        else:
            # if we are doing a buffered log
            if buffer:
                # add to buffer for folder
                self.buffered_log(msg=msg, folder=folder)
            # if we are not doing a buffered log
            else:
                self.unbuffered_log(msg=msg, folder=folder)

    def get_buffer(self):
        return self.sd_buffer

    def storage_stats(self):
        """
        return the storage statistics about the SD card and
        mainboard file system
        """
        sd_usage = None

        if self.cubesat.sdcard:
            # statvfs returns info about SD card (mounted file system)
            sd_storage_stats = statvfs(SD_DIR)
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

    def clear_logs(self):
        path = f"{SD_DIR}logs/"
        if "logs" in listdir(SD_DIR):
            # for all folders at the given path
            for folder in listdir(path):
                # remove each file
                for f in listdir(f"{path}{folder}"):
                    remove(f"{path}{folder}/{f}")
                # remove folder
                rmdir(f"{path}{folder}")
            rmdir(path)
