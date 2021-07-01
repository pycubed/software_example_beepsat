class Task:

    """
    The Task Object.

    Attributes:
        priority:    The priority level assigned to the task.
        frequency:   Number of times the task must be executed in 1 second (Hz).
        task_id:     User defined task identifier.
        schedule_later: If **True**, the task is scheduled after the first 'frequency' Hz interval.
    """

    priority = 10
    frequency = 1
    task_id = 1

    def __init__(self, satellite):
        """
        Initialise the Task by registering the cubesat object on it. 
        This is required to access the functionalities offered by the 
        PyCubed board.
        
        :type satellite: Satellite
        :param satellite: The cubesat to be registered

        """
        print('id: {}, freq: {}, priority: {}'.format(self.task_id,self.frequency,self.priority))
        self.cubesat = satellite

    async def main_task(self, *args, **kwargs):
        """
        Contains the code for the user defined task. 

        :param `*args`: Variable number of arguments used for task execution.
        :param `**kwargs`: Variable number of keyword arguments used for task execution. 

        """
        pass

    
