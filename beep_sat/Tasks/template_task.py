from debugcolor import co

class Task:

    """
    The Task Object.

    Attributes:
        priority:    The priority level assigned to the task.
        frequency:   Number of times the task must be executed in 1 second (Hz).
        name:        Name of the task object for future reference
    """

    priority = 10
    frequency = 1
    name = 'temp'
    color = 'gray'

    def __init__(self, satellite):
        """
        Initialize the Task using the PyCubed cubesat object.
        
        :type satellite: Satellite
        :param satellite: The cubesat to be registered

        """
        self.cubesat = satellite

    def debug(self,action,tabs=1):
        # print(co(msg='hello!',color='red'))
        print('{}{:>30}  {}'.format('\t'*tabs,'['+co(msg=self.name,color=self.color)+']',action))
        # print('{}{:>15}  {}'.format('\t'*tabs,'['+self.name+']',action))

    async def main_task(self, *args, **kwargs):
        """
        Contains the code for the user defined task. 

        :param `*args`: Variable number of arguments used for task execution.
        :param `**kwargs`: Variable number of keyword arguments used for task execution. 

        """
        pass

    
