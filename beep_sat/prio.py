#Test File for Priority Level Implementation
#Desired Output: All tasks execute in order of priorities, in all runs.
import builtins
builtins.tasko_logging = True

import tasko
import time

async def priority_one_task():
    print('P1 starting...')
    await tasko.sleep(1) # kinda busy
    print("  P1 finished.")

async def priority_two_task():
    print('P2 starting...')
    await tasko.sleep(1) # kinda busy
    print("  P2 finished.")

async def priority_three_task():
    print('P3 starting...')
    time.sleep(2) # simulate being very busy (blocking)
    print("  P3 finished.")

async def priority_four_task():
    print('P4 starting...')
    await tasko.sleep(1) # kinda busy
    print("  P4 finished.")

async def priority_five_task():
    print('P5 starting...')
    await tasko.sleep(1) # kinda busy
    print("  P5 finished.")


#Schedule tasks with desired priority
tasko.schedule(1, priority_one_task,    1)
tasko.schedule(1, priority_two_task,    2)
tasko.schedule(1, priority_three_task,  3)
tasko.schedule(1, priority_four_task,   4)
tasko.schedule(1, priority_five_task,   5)

tasko.run()
