from pycubed import pocketqube as cubesat
from pycubed_stats import incr_logfail_count
from os import listdir, stat, mkdir
import time

def check_sdcard():
    if cubesat.hardware['SDcard']:
        return True
    else:
        # increment nvm counter; tried to log without sd card being initialized
        incr_logfail_count()
        return False

def new_file(substring, binary=False):
    """
    create a new file on the SD card
    substring example: '/data/DATA_'
    int padded with zeroes will be appended to the last found file
    """

    """
    TO DO: move new_file function outside of pycubed.py
    """
    if check_sdcard():
        n = 0

        folder = substring[: substring.rfind('/') + 1]
        filen = substring[substring.rfind('/') + 1:]

        print('Creating new file in directory: /sd{} \
            with file prefix: {}'.format(folder, filen))

        # if the folder name is not currently in the sd directory,
        # create the directory and filename
        if folder.strip('/') not in listdir('/sd/'):
            print('Directory /sd{} not found. Creating...'.format(folder))
            mkdir('/sd' + folder)
            cubesat.filename = '/sd' + folder + filen + '000.txt'

        # if the folder name is currently in the sd directory
        else:
            # find the current maximum file number, n
            for f in listdir('/sd/' + folder):
                if filen in f:
                    for i in f.rsplit(filen):
                        # search .txt files specifically
                        if '.txt' in i and len(i) == 7:
                            c = i[-7: -4]
                            try:
                                if int(c) > n:
                                    n = int(c)
                            except ValueError:
                                continue

                            if int(i.rstrip('.txt')) > n:
                                n = int(i.rstrip('.txt'))
                                break

            # create new filepath in sd directory, using given
            # folder/file names
            cubesat.filename = (
                '/sd' + folder + filen + "{:03}".format(n + 1) + ".txt")

        # create new file with open, write timestamp and status
        with open(cubesat.filename, "a") as f:
            f.write(
                '# Created: {:.0f}\r\n# Status: {}\r\n'.format(
                    time.monotonic(), cubesat.status))

        # print a confirmation that this new file was created
        print('New self.filename:', cubesat.filename)
        return cubesat.filename

def log(msg):
    """
    create/open file and write logs
    """
    if check_sdcard():
        # if size of current open logfile > 100MB, create new log file
        if stat(cubesat.logfile)[6] > 1E8:
            cubesat.new_log()

        # open the current logfile and write message msg with a timestamp
        if cubesat.hardware['SDcard']:
            with open(cubesat.logfile, "a+") as file:
                file.write('{:.1f},{}\r\n'.format(time.monotonic(), msg))

def new_log():
    """
    create a new log file
    """
    if check_sdcard():
        n = 0

        # iterate through all files in the logs folder
        for f in listdir('/sd/logs/'):
            # if the file number is greater than n, set n to file number
            if int(f[3: -4]) > n:
                n = int(f[3: -4])

        # the new log file has number n + 1; n is the current
        # greatest file number
        cubesat.logfile = "/sd/logs/log" + "{:03}".format(n + 1) + ".txt"

        # open the new logfile and write the time it was created +
        # the current status
        with open(cubesat.logfile, "a") as log:
            log.write('# Created: {:.0f}\r\n# Status: {}\r\n'.format(
                time.monotonic(), cubesat.status))

        # print a confirmation message that a new logfile was created
        print('New log file:', cubesat.logfile)

def print_file(filedir=None):
    """
    DEBUGGING
    print a file given its directory; file directory is by default None
    """
    if check_sdcard():
        # if no file directory is passed, use the directory of the log file
        if filedir is None:
            filedir = cubesat.logfile

        print('--- Printing File: {} ---'.format(filedir))

        # open the current file directory as read only, print line by line
        # (removing whitespace)
        with open(filedir, "r") as file:
            for line in file:
                print(line.strip())

def save(dataset, savefile=None):
    """
    save the passed dataset to the passed savefile
    dataset should be a set of lists; each line is a list:
        save(([line1],[line2]))
    to save a string, make it an item in a list:
        save(['This is my string'])
    by default, savefile is not passed
    """
    if check_sdcard():
        # if no savefile is passed, use the current filename attribute
        # by default
        if savefile is None:
            savefile = cubesat.filename

        # open save file
        try:
            with open(savefile, "a") as file:
                for item in dataset:
                    # if the item is a list or tuple
                    if isinstance(item, (list, tuple)):
                        # iterate through item
                        for i in item:
                            # format based on whether i is a float or not
                            try:
                                if isinstance(i, float):
                                    file.write('{:.9g},'.format(i))
                                else:
                                    file.write('{:G},'.format(i))
                            except Exception:
                                file.write('{},'.format(i))
                    # if the item is not a list or tuple, format
                    else:
                        file.write('{},'.format(item))

                    # write a newline to the file
                    file.write('\n')

        # catch exception
        except Exception as e:
            # print SD save error message with exception
            print('[ERROR] SD Save:', e)
            cubesat.RGB = (255, 0, 0)  # set RGB to red
            return False
