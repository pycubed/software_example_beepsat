# Task to send "Hello World" on the radio

from Tasks.template_task import Task

class task(Task):
    priority = 1
    frequency = 1/10
    name='listen'
    color = 'teal'

    schedule_later=True

    async def main_task(self):
        # run once at the start
        self.debug('Listening')
        self.cubesat.radio1.listen()

        await self.cubesat.radio1.await_rx(timeout=5)

        self.debug('done awaiting rx')
        msg = self.cubesat.radio1.receive(keep_listening=True)
        if msg is not None:
            self.debug("Heard: {}".format(msg),2)

        self.cubesat.scheduled_tasks['listen'].stop()




