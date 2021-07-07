# check for low battery condition

from Tasks.template_task import Task
import time

class task(Task):
    priority = 3
    frequency = 1/10 # once every 10s
    name='vbatt'
    color = 'orange'

    timeout=60*60 # 60 min

    def wakeup(self):
        self.cubesat.powermode('normal')
        # restart all tasks
        for t in self.cubesat.scheduled_tasks:
            self.cubesat.scheduled_tasks[t].stop()

    async def main_task(self):
        vbatt=self.cubesat.battery_voltage
        comp_var = ''

        if vbatt > self.cubesat.vlowbatt:
            comp_var = '>'
        else:
            comp_var = '<'

        self.debug('{:.1f}V {} threshold: {:.1f}V'.format(vbatt,comp_var,self.cubesat.vlowbatt))

        # TODO this should go in a more advanced beep sat example?
        # if vbatt < self.cubesat.vlowbatt:
        #     self.cubesat.f_lowbatt=True
        #     if self.cubesat.f_lowbtout:
        #         self.debug('lowbatt timeout flag set! skipping...')
        #     else:
        #         _timer=time.monotonic()+self.timeout
        #         self.debug('low battery detected!')
        #         # stop all tasks
        #         for t in self.cubesat.scheduled_tasks:
        #             self.cubesat.scheduled_tasks[t].stop()

        #         self.cubesat.powermode('minimum')
        #         while time.monotonic() < _timer:
        #             time.sleep(self.timeout/10)
        #             vbatt=self.cubesat.battery_voltage
        #             if vbatt > self.cubesat.vlowbat:
        #                 self.debug('batteries above threshold')
        #                 self.cubesat.f_lowbatt=False
        #                 break

        #             if time.monotonic() > _timer:
        #                 self.debug('timed out!')
        #                 # set timeout flag so we know to bypass
        #                 self.cubesat.f_lowbtout = True
        #                 # log (if we can)
        #                 try: self.cubesat.log(',lb')
        #                 except: pass
        #                 break

        #         # always wake up
        #         self.wakeup()




