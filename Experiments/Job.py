import os
import traceback
from enum import Enum

class JobStatus(str, Enum):
    INITIALISED = "initialised"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"

class Job:
    """
    Represents a job.

    Attributes:
        id (int): The job's identifier.
        params (dict): A dictionary of hyper-parameters for the job.
        status (str): The job's status. One of 'INITIALISED', 'RUNNING', 'FAILED' or 'DONE'.
        output_path (str): Path to folder where the jobs output and results shall be stored.
        status_path (str): Path to file that stores the status persistently.
        log_path (str): Path to file that stores the logging.
    """

    def __init__(self, id: int, path: str, params: dict = None, status: JobStatus = JobStatus.INITIALISED):
        """
        Initialises a job.

        Args:
            id (int): The job's identifier (a natural number).
            path (int): Path to the job's storage folder.
            params (dict): A dictionary of job parameters.
            status (JobStatus): The job's status. Default is 'initialised'.
        """
        self.id = id

        if params is None:
            params = {}
        self.params = params

        self.status = status

        self.output_path = os.path.join(path, "experiments", str(id))
        self.status_path = os.path.join(path, "experiments", str(id), "status.txt")
        self.log_path    = os.path.join(path, "experiments", str(id), "log.txt")
        self._create_paths()

    def _create_paths(self) -> None:
        """
        Creates the jobs' files.

        Internally creates files that store the jobs status and logs.
        """
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
            with open(self.status_path, "w") as file:
                file.write(self.status)
            with open(self.log_path, "w") as file:
                file.write("")

    def get_outout_path(self) -> str:
        """
        Return the output path.

        Returns:
            File path to the output folder.
        """
        return self.output_path

    def get_id(self) -> int:
        """
        Return job identifier.

        Returns:
            The job ID is returned.
        """
        return self.id


    def get_params(self) -> dict:
        """
        Return the job's parameters.

        Returns:
            A dictionary of parameters. The parameter names are the keys while the values are parameters.
        """
        return self.params
    

    def get_param_names(self) -> list[str]:
        """
        Return the names of the parameters.
        
        Returns:
            List of strings.
        """
        return list(self.params.keys())


    def get_status(self) -> JobStatus:
        """
        Return status.

        Returns:
            The job's status.
        """
        return self.status


    def set_done(self) -> None:
        """
        Set job to finished/done.
        """
        self._update_status(JobStatus.DONE)


    def set_running(self) -> None:
        """
        Set job to running.
        """
        self._update_status(JobStatus.RUNNING)


    def set_failed(self) -> None:
        """
        Set job to failed.
        """
        self._update_status(JobStatus.FAILED)


    def is_done(self) -> bool:
        """
        Is the job finished/done?

        Returns:
            Boolean indicating if the job has successfully finished.
        """
        return self.status == JobStatus.DONE


    def is_failed(self) -> bool:
        """
        Is the job failed?

        Returns:
            Boolean indicating if the job has failed. See its logs for details in this case.
        """
        return self.status == JobStatus.FAILED


    def is_running(self) -> bool:
        """
        Is the job running?

        Returns:
            Boolean indicating if the job is currently being executed.
        """
        return self.status == JobStatus.RUNNING


    def is_initialised(self) -> bool:
        """
        Is the job initialised?

        Returns:
            Boolean indicating if the job has not yet been started.
        """
        return self.status == JobStatus.INITIALISED


    def _update_status(self, status: JobStatus) -> None:
        """
        Update the job's status.
        
        Args:
            status (JobStatus): The new status.
        """
        self.status = status
        with open(self.status_path, "w") as file:
            file.write(self.status)


    def read_status(self) -> None:
        """
        Read the job's status from file.
        """

        with open(self.status_path, "r") as file:
            self.status = file.read()


    def log(self, e: Exception):
        """
        Write to the job's log.
        
        Args:
            e (Exception): An exception object. The traceback is written to the job's log-file.
        """

        with open(self.log_path, "w") as file:
            traceback.print_exc(file = file)


    def __str__(self) -> str:
        """
        Represent job as a string.
        """
        return f"#{self.id} (params: {len(self.params) - 1}, status: '{self.status}')"
