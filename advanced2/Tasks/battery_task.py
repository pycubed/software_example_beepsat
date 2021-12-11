# check for low battery condition

from Tasks.template_task import Task
import time

class task(Task):
    priority = 3
    frequency = 1/10 # once every 10s
    name='vbatt'
    color = 'orange'

    async def main_task(self):
        THRESHOLD   = self.cubesat.cfg['lb']
        LOW_BATTERY = True # default to true as fail-safe
        vbatt=self.cubesat.battery_voltage

        if vbatt > THRESHOLD:
            LOW_BATTERY = False
            # clear all our low battery flags and counter
            if self.cubesat.f_lowbatt:
                self.cubesat.f_lowbatt=False
                self.cubesat.f_lowbtout=False
                self.cubesat.c_lowb=0
        elif not self.cubesat.f_lowbtout:
            """
            LOW BATTERY CONDITION!!
            we don't want to get stuck in low battery mode, so we need to
            count how many times we hit this condition. we have to use an
            NVM counter since RAM gets reset during deep sleep
            """
            self.cubesat.c_lowb+=1
            self.debug(f'incrementing c_lowb to {self.cubesat.c_lowb}')

            if self.cubesat.c_lowb > 4:
                # default 12hr deep sleep = 4*12 = 48hr before timeout
                self.debug('c_lowb reached. setting lowbatt timeout flag')
                self.cubesat.f_lowbtout=True

        self.debug(f'{vbatt:.1f}V {'<' if LOW_BATTERY else '>'} threshold: {THRESHOLD:.1f}V')

        ########### ADVANCED ###########
        # respond to a low power condition
        if LOW_BATTERY:
            self.cubesat.f_lowbatt=True
            # if we've timed out, don't do anything
            if self.cubesat.f_lowbtout:
                self.debug('lowbatt timeout flag set! skipping...')
            else:
                self.debug('low battery detected!',2)
                # stop all tasks
                for t in self.cubesat.scheduled_tasks:
                    self.cubesat.scheduled_tasks[t].stop()

                self.cubesat.powermode('minimum')

                # configure for deep sleep, default 12hrs
                if 'st' in self.cubesat.cfg:
                    _sleeptime = self.cubesat.cfg['st']
                else:
                    _sleeptime=5
                import alarm, board
                _sleeptime = eval('0.432e'+str(_sleeptime)) # default 0.432e5 = 43200s = 12hrs
                time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + _sleeptime)
                alarm.exit_and_deep_sleep_until_alarms(time_alarm)
                # board will deep sleep until time_alarm then reset
                # no further code will run!!
