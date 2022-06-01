import traceback
from lib.pycubed import pocketqube as cubesat
import state_machine


print('Running...')
try:
    # should run forever
    _ = state_machine.StateMachine(cubesat, 'Normal')
except Exception as e:
    formated_exception = traceback.format_exception(e, e, e.__traceback__)
    for line in formated_exception:
        print(line, end='')

    try:
        # increment our NVM error counter
        cubesat.c_state_err += 1
        # try to log everything
        cubesat.log(f'{formated_exception},{cubesat.c_state_err},{cubesat.c_boot}')
    except:
        pass

# we shouldn't be here!
print('Engaging fail safe: hard reset')
# from time import sleep
# sleep(10)
# cubesat.micro.on_next_reset(cubesat.micro.RunMode.NORMAL)
# cubesat.micro.reset()
