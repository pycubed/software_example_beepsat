class StopTask:
    """
    
    The StopTask object that is used to stop tasks from within a task.

    """
    def __init__(self, satellite, num_of_tasks, task_ids):
        """
        Initialise the StopTask object by regsitering the cubesat on it.
        This is required to access the list of scheduled task objects from which 
        the appropriate tasks are stopped.

        :type satellite: Satellite
        :param satellite: The cubesat to be registered

        :type num_of_tasks: int
        :param num_of_tasks: The number of tasks to be stopped

        :type task_ids: list of int
        :param task_ids: A list containing the integer task_ids of the tasks to be stopped

        """
        self.cubesat = satellite
        self.num = num_of_tasks
        self.task_id_list = task_ids
        self.count = 0

    def stop(self):
        """
        Object method that is used to stop the tasks specified by the parameters provided during initialisation.
        
        """
        for task in self.cubesat.scheduled_objects:
            if task.get_task_id() in self.task_id_list:
                task.stop()
                self.count = self.count + 1
        assert self.count == self.num, "Multiple tasks have the same task_id!"
