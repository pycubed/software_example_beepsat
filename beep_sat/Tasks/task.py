class Task:

    """
    The Task Object.

    Attributes:
        priority:    The priority level assigned to the task.
        frequency:   Number of times the task must be executed in 1 second (Hz).
        task_id:     User defined task identifier.
        schedule_later: If **True**, the task is scheduled after the first 'frequency' Hz interval.
    """

    priority: int = 3
    frequency: float = 1
    task_id: int = 3
    schedule_later: bool=False

    def __init__(self, satellite):
        """
        Initialise the Task by registering the cubesat object on it. 
        This is required to access the functionalities offered by the 
        PyCubed board.
        
        :type satellite: Satellite
        :param satellite: The cubesat to be registered

        """

        self.cubesat = satellite

    async def main_task(self, *args, **kwargs):
        """
        Contains the code for the user defined task. 

        :param `*args`: Variable number of arguments used for task execution.
        :param `**kwargs`: Variable number of keyword arguments used for task execution. 

        """
        print("Sending message from PyCubed....")
        self.cubesat.radio2.send("Hello World!", keep_listening=True)
        print("Message sent from PyCubed")

    
