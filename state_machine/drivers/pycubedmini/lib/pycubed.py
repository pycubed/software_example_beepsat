"""
CircuitPython driver for PyCubed satellite board
PyCubed Mini mainboard-v02 for Pocketqube Mission
* Author(s): Max Holliday, Yashika Batra
"""

import sdcardio
import pycubed_rfm9x
import board
import microcontroller
import busio
import time
import digitalio
import analogio
import storage
import sys
import neopixel
import pwmio
import bmx160
import drv8830
from os import listdir, stat, statvfs, mkdir
from bitflags import bitFlag, multiBitFlag
from micropython import const
import adafruit_tsl2561

# NVM register numbers
# TODO: confirm registers start in MRAM partition & update board build file
_FLAG = const(20)
_DWNLINK = const(4)
_DCOUNT = const(3)
_RSTERRS = const(2)
_BOOTCNT = const(0)


class Satellite:
    # Define NVM flags
    f_deploy = bitFlag(register=_FLAG, bit=1)
    f_mdeploy = bitFlag(register=_FLAG, bit=2)
    f_burn1 = bitFlag(register=_FLAG, bit=3)
    f_burn2 = bitFlag(register=_FLAG, bit=4)

    # Define NVM counters
    c_boot = multiBitFlag(register=_BOOTCNT, lowest_bit=0, num_bits=8)
    c_state_err = multiBitFlag(register=_RSTERRS, lowest_bit=4, num_bits=4)
    c_vbus_rst = multiBitFlag(register=_RSTERRS, lowest_bit=0, num_bits=4)
    c_deploy = multiBitFlag(register=_DCOUNT, lowest_bit=0, num_bits=8)
    c_downlink = multiBitFlag(register=_DWNLINK, lowest_bit=0, num_bits=8)

    # change to 433?
    UHF_FREQ = 433.0

    def __init__(self, test_mode=False):
        """ Big init routine as the whole board is brought up. """

        # Initialize test_mode variable. If true, print extra information
        self.test_mode = test_mode

        if self.test_mode:
            print("Initializing PyCubedMini Hardware...")

        self._stat = {}
        self.BOOTTIME = const(self.timeon)

        # Initialize hardware dictionary
        self.hardware = {
            'IMU':    False,
            'Radio':  False,
            'SDcard': False,
            'GPS':    False,
            'WDT':    False,
            'Sun':    False,
            'Coils':  False,
            'BurnWire': False,
        }

        # Print the initial state of this hardware dictionary
        if self.test_mode:
            print("Hardware:", str(self.hardware))

        self.micro = microcontroller

        self.data_cache = {}
        self.filenumbers = {}
        self.vlowbatt = 3.5
        self.debug = True

        # Define battery voltage
        self._vbatt = analogio.AnalogIn(board.BATTERY)

        # Define SPI,I2C,UART
        self.i2c1 = busio.I2C(board.SCL1, board.SDA1)
        self.i2c2 = busio.I2C(board.SCL2, board.SDA2)
        self.i2c3 = busio.I2C(board.SCL3, board.SDA3)
        self.spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        # self.spi = board.SPI()

        if self.test_mode:
            print("Initialized I2C1, I2C2, I2C3, SPI")

        # Define sdcard
        self.filename = "/sd/default.txt"
        self.logfile = "/sd/logs/log000.txt"
        # self.current_logfilenum = 0
        if self.test_mode:
            print("Defined initial SD Card filenames and logfiles")

        # Define radio
        self._rf_cs = digitalio.DigitalInOut(board.RF_CS)
        self._rf_rst = digitalio.DigitalInOut(board.RF_RST)
        self.radio_DIO0 = digitalio.DigitalInOut(board.RF_IO0)
        self.radio_DIO0.switch_to_input()
        self.radio_DIO1 = digitalio.DigitalInOut(board.RF_IO1)
        self.radio_DIO1.switch_to_input()
        self._rf_cs.switch_to_output(value=True)
        self._rf_rst.switch_to_output(value=True)
        if self.test_mode:
            print("Defined radio")

        # Initialize Neopixel
        try:
            self.neopixel = neopixel.NeoPixel(
                board.NEOPIXEL, 1, brightness=0.2, pixel_order=neopixel.GRB)
            self.neopixel[0] = (0, 0, 0)
            self.hardware['Neopixel'] = True
            if self.test_mode:
                print("Initialized Neopixel")
        except Exception as e:
            print('[WARNING][Neopixel]', e)

        # Initialize sdcard
        try:
            self._sd = sdcardio.SDCard(self.spi, board.CS_SD, baudrate=4000000)
            self._vfs = storage.VfsFat(self._sd)
            storage.mount(self._vfs, "/sd")
            sys.path.append("/sd")
            self.hardware['SDcard'] = True
            if self.test_mode:
                print("Initialized SD Card SPI and Virtual File System (VFS)")
            # self.new_log() # create new log file
        except Exception as e:
            print('[ERROR][SD Card]', e)

        # Initialize radio - UHF
        try:
            self.radio = pycubed_rfm9x.RFM9x(
                self.spi, self._rf_cs, self._rf_rst,
                self.UHF_FREQ, rfm95pw=True)
            self.radio.dio0 = self.radio_DIO0
            self.radio.sleep()
            self.hardware['Radio'] = True
            if self.test_mode:
                print("Initialized Radio")
        except Exception as e:
            print('[ERROR][RADIO]', e)

        # Initialize IMU
        try:
            self.IMU = bmx160.BMX160_I2C(self.i2c1, address=0x68)
            self.hardware['IMU'] = True
            if self.test_mode:
                print("Initialized IMU")
        except Exception as e:
            print(f'[ERROR][IMU] {e}\n\tMaybe try address=0x68?')

        # Initialize Sun Sensors
        sun_sensors = self.__init_sun_sensors()
        # If there is at least one sun sensor, set to True
        if len(sun_sensors) >= 1:
            self.hardware['Sun'] = True

        # Initialize H-Bridges
        coils = self.__init_coil_drivers()
        # If there is at least one coil, set to True
        if len(coils) >= 1:
            self.hardware['Coils'] = True

        # Initialize burnwires
        burnwires = self.__init_burnwires()
        # If there is at least one burnwire, set to True
        if len(burnwires) >= 1:
            self.hardware['BurnWire'] = True

    def __init_sun_sensors(self):
        sun_sensors = []

        try:
            sun_yn = adafruit_tsl2561.TSL2561(self.i2c2, address=0x29)  # -Y
            sun_sensors.append(sun_yn)
            if self.test_mode:
                print("Initialized -Y Sensor")
        except Exception as e:
            print('[ERROR][Sun Sensor -Y]', e)

        try:
            sun_zn = adafruit_tsl2561.TSL2561(self.i2c2, address=0x39)  # -Z
            sun_sensors.append(sun_zn)
            if self.test_mode:
                print("Initialized -Z Sensor")
        except Exception as e:
            print('[ERROR][Sun Sensor -Z]', e)

        try:
            sun_xn = adafruit_tsl2561.TSL2561(self.i2c1, address=0x49)  # -X
            sun_sensors.append(sun_xn)
            if self.test_mode:
                print("Initialized -X Sensor")
        except Exception as e:
            print('[ERROR][Sun Sensor -X]', e)

        try:
            sun_yp = adafruit_tsl2561.TSL2561(self.i2c1, address=0x29)  # +Y
            sun_sensors.append(sun_yp)
            if self.test_mode:
                print("Initialized +Y Sensor")
        except Exception as e:
            print('[ERROR][Sun Sensor +Y]', e)

        try:
            sun_zp = adafruit_tsl2561.TSL2561(self.i2c1, address=0x39)  # +Z
            sun_sensors.append(sun_zp)
            if self.test_mode:
                print("Initialized +Z Sensor")
        except Exception as e:
            print('[ERROR][Sun Sensor +Z]', e)

        try:
            sun_xp = adafruit_tsl2561.TSL2561(self.i2c2, address=0x49)  # +X
            sun_sensors.append(sun_xp)
            if self.test_mode:
                print("Initialized +X Sensor")
        except Exception as e:
            print('[ERROR][Sun Sensor +X]', e)

        for i in sun_sensors:
            i.enabled = False  # set enabled status to False
            if self.test_mode:
                print("Sensor", i, "enabled status is", i.enabled)

        return sun_sensors

    def __init_coil_drivers(self):
        coils = []

        try:
            drv_x = drv8830.DRV8830(self.i2c3, 0x68)  # U6
            coils.append(drv_x)
            if self.test_mode:
                print("Initialized Driver X")
        except Exception as e:
            print('[ERROR][H-Bridge U6]', e)

        try:
            drv_y = drv8830.DRV8830(self.i2c3, 0x60)  # U8
            coils.append(drv_y)
            if self.test_mode:
                print("Initialized Driver Y")
        except Exception as e:
            print('[ERROR][H-Bridge U8]', e)

        try:
            drv_z = drv8830.DRV8830(self.i2c3, 0x62)  # U4
            coils.append(drv_z)
            if self.test_mode:
                print("Initialized Driver Z")
        except Exception as e:
            print('[ERROR][H-Bridge U4]', e)

        driver_count = 0
        for driver in coils:
            driver.mode = drv8830.COAST
            driver.vout = 0
            if self.test_mode:
                driver_count += 1
                if driver_count == 1:
                    driver_str = "Driver X"
                elif driver_count == 2:
                    driver_str = "Driver Y"
                elif driver_count == 3:
                    driver_str = "Driver Z"
                print(driver_str, "mode: COAST, voltage out: ", driver.vout)

        return coils

    def __init_burnwires(self):
        burnwires = []

        try:
            # changed pinout from BURN1 to PA15 (BURN1 did not support PWMOut)
            self.burnwire1 = pwmio.PWMOut(
                microcontroller.pin.PA15, frequency=1000, duty_cycle=0)
            burnwires.append(self.burnwire1)
            if self.test_mode:
                print("Initialized Burnwire Pin 1")
        except Exception as e:
            print('[ERROR][Burn Wire IC1]', e)

        try:
            # changed pinout from BURN2 to PA15 (BURN2 did not support PWMOut)
            self.burnwire2 = pwmio.PWMOut(
                microcontroller.pin.PA18, frequency=1000, duty_cycle=0)
            burnwires.append(self.burnwire2)
            if self.test_mode:
                print("Initialized Burnwire Pin 2")
        except Exception as e:
            print('[ERROR][Burn Wire IC1]', e)

        return burnwires

    def reinit(self, dev):
        """
        reinit: reinitialize radio, sd, or IMU based upon contents of dev
        """
        # dev is a string of all lowercase letters,
        dev = dev.lower()

        # reinitialize device based on string dev
        if dev == 'radio':
            # should we be reinitializing radio2 or just radio?
            self.radio.__init__(
                self.spi, self._rf_cs, self._rf_rst, self.UHF_FREQ)
        elif dev == 'sd':
            self._sd.__init__(self.spi, self._sdcs, baudrate=1000000)
        elif dev == 'imu':
            self.IMU.__init__(self.i2c1)
        else:
            print('Invalid Device? ->', dev)

    @property
    def acceleration(self):
        """
        return the accelerometer reading from the IMU
        """
        return self.IMU.accel

    @property
    def magnetic(self):
        """
        return the magnetometer reading from the IMU
        """
        return self.IMU.mag

    @property
    def gyro(self):
        """
        return the gyroscope reading from the IMU
        """
        return self.IMU.gyro

    @property
    def temperature(self):
        """
        return the thermometer reading from the IMU
        """
        return self.IMU.temperature  # Celsius

    @property
    def temperature_cpu(self):
        """
        return the temperature reading from the CPU
        """
        return microcontroller.cpu.temperature  # Celsius

    @property
    def RGB(self):
        """
        return the current RBG settings of the neopixel object
        """
        return self.neopixel[0]

    @RGB.setter
    def RGB(self, value):
        """
        set an RGB value to the neopixel object
        """
        if self.hardware['Neopixel']:
            try:
                self.neopixel[0] = value
            except Exception as e:
                print('[WARNING]', e)

    @property
    def battery_voltage(self):
        """
        return the battery voltage
        """
        # initialize vbat
        vbat = 0

        for _ in range(50):
            # 65536 = 2^16, number of increments we can have to voltage
            vbat += self._vbatt.value * 3.3 / 65536

        # 100k/100k voltage divider
        voltage = (vbat / 50) * (100 + 100) / 100

        # volts
        return voltage

    @property
    def fuel_gauge(self):
        """
        report battery voltage as % full
        """
        return 100 * self.battery_voltage / 4.2

    @property
    def reset_boot_count(self):
        """
        reset boot count in non-volatile memory (nvm)
        """
        microcontroller.nvm[0] = 0

    @property
    def status(self):
        """
        return a dictionary with the following:
        1. NVM registers(boot count, flags, counters)
        2. Time (seconds) since boot/hard reset
        3. Battery voltage as % of full
        """

        self._stat.update({
            'boot-time': self.BOOTTIME,
            'boot-count': self.c_boot,
            'time-on': self.timeon,
            'fuel-gauge': self.fuel_gauge,
            'flags': {
                'deploy': self.f_deploy,
                'mid-deploy': self.f_mdeploy,
                'burn1': self.f_burn1,
                'burn2': self.f_burn2
            },
            'counters': {
                'state-errors': self.c_state_err,
                'vbus-resets': self.c_vbus_rst,
                'deploy': self.c_deploy,
                'downlink': self.c_downlink,
            },
        })

        self._stat.update({
            'raw': bytes
            ([
                self.micro.nvm[_BOOTCNT],
                self.micro.nvm[_FLAG],
                self.micro.nvm[_RSTERRS],
                self.micro.nvm[_DWNLINK],
                self.micro.nvm[_DCOUNT]
            ]) +
            self.BOOTTIME.to_bytes(3, 'big') +
            self._stat['time-on'].to_bytes(4, 'big') +
            int(self._stat['fuel-gauge']).to_bytes(1, 'big')
        })

        return self._stat

    @property
    def timeon(self):
        """
        return the time on a monotonic clock
        """
        return int(time.monotonic())

    def crc(self, data):
        """
        cyclic redundancy check (crc)
        """
        crc = 0

        # hash function: xor each byte with current crc and return
        for byte in data:
            crc ^= byte

        return crc

    def new_file(self, substring, binary=False):
        """
        create a new file on the SD card
        substring example: '/data/DATA_'
        int padded with zeroes will be appended to the last found file
        """
        if self.hardware['SDcard']:
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
                self.filename = '/sd' + folder + filen + '000.txt'

            # if the folder name is currently in the sd directory
            else:
                # find the current maximum file number, n
                # loop through every file in the given sd card folder
                for f in listdir('/sd/' + folder):
                    # if the filename we're looking for is in the current file
                    if filen in f:
                        # split string filen into list, use filen as delimeter
                        for i in f.rsplit(filen):
                            # search .txt files specifically
                            if '.txt' in i and len(i) == 7:
                                # index 7-7 to 7-4 -- index 0 to 3
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
                self.filename = (
                    '/sd' + folder + filen + "{:03}".format(n + 1) + ".txt")

            # create new file with open, write timestamp and status
            with open(self.filename, "a") as f:
                f.write(
                    '# Created: {:.0f}\r\n# Status: {}\r\n'.format(
                        time.monotonic(), self.status))

            # print a confirmation that this new file was created
            print('New self.filename:', self.filename)
            return self.filename

    @property
    def storage_stats(self):
        """
        return the storage statistics about the SD card and
        mainboard file system
        """
        sd = 0
        if self.hardware['SDcard']:
            # statvfs returns info about SD card (mounted file system)
            sd = statvfs('/sd/')
            sd = int(100 * sd[3] / sd[2])

        # returns information about the overall file system
        fs = statvfs('/')
        fs = int(100 * fs[3] / fs[2])

        # return both sets of information
        return (fs, sd)

    def log(self, msg):
        """
        create/open file and write logs
        """

        # if size of current open logfile > 100MB, create new log file
        if stat(self.logfile)[6] > 1E8:
            self.new_log()

        # open the current logfile and write message msg with a timestamp
        if self.hardware['SDcard']:
            with open(self.logfile, "a+") as file:
                file.write('{:.1f},{}\r\n'.format(time.monotonic(), msg))

    def new_log(self):
        """
        create a new log file
        """
        if self.hardware['SDcard']:
            n = 0

            # iterate through all files in the logs folder
            for f in listdir('/sd/logs/'):
                # if the file number is greater than n, set n to file number
                if int(f[3: -4]) > n:
                    n = int(f[3: -4])

            # the new log file has number n + 1; n is the current
            # greatest file number
            self.logfile = "/sd/logs/log" + "{:03}".format(n + 1) + ".txt"

            # open the new logfile and write the time it was created +
            # the current status
            with open(self.logfile, "a") as log:
                log.write('# Created: {:.0f}\r\n# Status: {}\r\n'.format(
                    time.monotonic(), self.status))

            # print a confirmation message that a new logfile was created
            print('New log file:', self.logfile)

    def print_file(self, filedir=None):
        """
        print a file given its directory; file directory is by default None
        """

        # if no file directory is passed, use the directory of the log file
        if filedir is None:
            filedir = self.logfile

        print('--- Printing File: {} ---'.format(filedir))

        # open the current file directory as read only, print line by line
        # (removing whitespace)
        with open(filedir, "r") as file:
            for line in file:
                print(line.strip())

    def send_file(self, c_size, send_buffer, filename):
        """
        send a file given character size, buffer size, and the filename
        """

        # number of packets is the size of the filename / character size
        num_packets = int(stat(filename)[6] / c_size)

        # open the file
        with open(filename, "rb") as f:
            # for each packet
            for i in range(num_packets + 1):
                # move the cursor to the end of i * character size,
                # add to buffer
                f.seek(i * c_size)
                f.readinto(send_buffer)

                # return bytes; yield keyword returns without destroying
                # states of local vars
                yield bytes([i, 0x45, num_packets])

    def save(self, dataset, savefile=None):
        """
        save the passed dataset to the passed savefile
        dataset should be a set of lists; each line is a list:
            save(([line1],[line2]))
        to save a string, make it an item in a list:
            save(['This is my string'])
        by default, savefile is not passed
        """
        # if no savefile is passed, use the current filename attribute
        # by default
        if savefile is None:
            savefile = self.filename

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
            self.RGB = (255, 0, 0)  # set RGB to red
            return False

    def fifo(self, data, item):
        """
        First-in first-out buffer
        Buffer must be a list, size will not change.
        preallocation example: data = [bytes([0] * 66)] * 30
        """
        del data[0]
        data.append(item)

    def burn(self, burn_num, dutycycle=0, freq=1000, duration=1):
        """ control the burnwire(s) """
        # BURN1 = -Z,BURN2 = extra burnwire pin, dutycycle ~0.13%
        dtycycl = int((dutycycle / 100) * (0xFFFF))

        # print configuration information
        print('----- BURN WIRE CONFIGURATION -----')
        print(f'\tFrequency of: {freq}Hz')
        print(f'\tDuty cycle of: {100 * dtycycl / 0xFFFF}% (int:{dtycycl})')
        print(f'\tDuration of {duration}sec')

        # initialize burnwire based on the burn_num passed to the function
        if '1' in burn_num:
            burnwire = self.burnwire1
        elif '2' in burn_num:
            burnwire = self.burnwire2
        else:
            return False

        self.RGB = (255, 0, 0)  # set RGB to red

        # set the burnwire's dutycycle; begins the burn
        burnwire.duty_cycle = dtycycl
        time.sleep(duration)  # wait for given duration

        # set burnwire's dutycycle back to 0; ends the burn
        burnwire.duty_cycle = 0
        self.RGB = (0, 0, 0)  # set RGB to black / no color

        self._deployA = True  # sets deployment variable to true
        burnwire.deinit()  # deinitialize burnwire

        return self._deployA  # return true


# initialize Satellite as pocketqube
# pocketqube = Satellite()
