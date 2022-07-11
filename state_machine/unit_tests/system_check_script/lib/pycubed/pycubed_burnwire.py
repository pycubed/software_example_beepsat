"""
CircuitPython driver for PyCubed satellite board burnwire control
PyCubed Mini mainboard-v02 for Pocketqube Mission
* Author(s): Max Holliday, Yashika Batra
"""
from pycubed import pocketqube as cubesat
from pycubed_logging import log
import time


if cubesat.hardware['Burn Wire 1'] or cubesat.hardware['Burn Wire 2']:
    def burn(burn_num='1', dutycycle=0, freq=1000, duration=1):
        """
        control the burnwire(s)
        initialize with burn_num = '1' ; burnwire 2 IC is not set up
        """

        # BURN1 = -Z,BURN2 = extra burnwire pin, dutycycle ~0.13%
        dtycycl = int((dutycycle / 100) * (0xFFFF))

        # print configuration information
        print('----- BURN WIRE CONFIGURATION -----')
        print(f'\tFrequency of: {freq}Hz')
        print(f'\tDuty cycle of: {100 * dtycycl / 0xFFFF}% (int:{dtycycl})')
        print(f'\tDuration of {duration}sec')

        # initialize burnwire based on the burn_num passed to the function
        if '1' in burn_num:
            burnwire = cubesat.burnwire1
        elif '2' in burn_num:
            return False  # return False because burnwire 2 IC is not set up
            # burnwire = self.burnwire2
        else:
            return False

        cubesat.RGB = (255, 0, 0)  # set RGB to red

        # set the burnwire's dutycycle; begins the burn
        burnwire.duty_cycle = dtycycl
        time.sleep(duration)  # wait for given duration

        # set burnwire's dutycycle back to 0; ends the burn
        burnwire.duty_cycle = 0
        cubesat.RGB = (0, 0, 0)  # set RGB to no color

        cubesat._deployA = True  # sets deployment variable to true
        burnwire.deinit()  # deinitialize burnwire

        return cubesat._deployA  # return true
else:
    log("Burnwire accessed without being initialized")
