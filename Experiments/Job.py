import os
import shutil
import traceback
import pickle
from enum import Enum
from typing import Self

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
        result_path (str): Path to pickle file that stores the job functions result / return value.
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
            result (any): The job's result.
        """
        self.id = id

        if params is None:
            params = {}
        self.params = params
        self.tags = set()
        self.status = status
        self.result = None
        self.runtime = None

        self.path = path
        self.output_path = os.path.join(path, "experiments", str(id))
        self.pickle_path = os.path.join(path, "experiments", str(id), "job.pkl")
        self.result_path = os.path.join(path, "experiments", str(id), "result")
        self.log_path    = os.path.join(path, "experiments", str(id), "log.txt")
        self._create_paths()


    def _create_paths(self) -> None:
        """
        Creates the jobs' files.

        Internally creates files that store the jobs status and logs.
        """
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
            with open(self.log_path, "w") as file:
                file.write("")


    def clear_log(self) -> Self:
        """
        Clears the job's log.
        """
        with open(self.log_path, "w") as file:
            file.write("")


    def tag(self, tags: list[str]) -> Self:
        """
        Adds tags to jobs.

        Args:
            tags (list[str]): list of tags. Each tag is a string.
        Returns:
            The callee itself (enables chaining).
        """
        self.tags = self.tags.union(set(tags))

    
    def has_tags(self, tags: list[str]) -> bool:
        """
        Check if job contains certain tags.

        Args:
            tags (list[str]): list of tags. Each tag is a string.
        Returns:
            A Boolean that is True if the job has all tags appended and False otherwise.
        """        
        return self.tags.issuperset(tags)


    def reset(self) -> Self:
        """
        Resets the job to the 'initialised' state.

        Returns:
            The callee itself (enables chaining).
        """
        # Remove all stored data
        shutil.rmtree(self.output_path, ignore_errors = True)

        # Recreate 
        self._create_paths()

        # Reset status
        self.set_initialised()
        self.runtime = None

        print(f"Reset job #'{self.id}'")

        return self


    def get_output_path(self) -> str:
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
    

    def get_result(self, simplify: bool = False) -> tuple[int, dict[str, any], dict[str, any]] | dict[str, any]:
        """
        Return job result.

        Args:
            simplify (bool): Should the result be returned as a single dictionary? Default is 'False'.

        Returns:
            The result of the job either as a 3-tuple (jobid, params, result) or a dictionary (dict[str, any])
            if simplify is set to 'True'.      
        """
        if self.result is None and self.status == JobStatus.DONE:
            try:
                with open(self.result_path, "rb") as file:
                    self.result = pickle.load(file)
            except Exception as e:
                raise Exception(f"Job #'{self.get_id()}' is 'DONE', but result is unavailable.")       

        if simplify:
            return {"jobid": self.get_id()} | self.get_params() | self.result

        return (self.get_id(), self.get_params(), self.result)
    

    def set_result(self, result: any) -> Self:
        """
        Set job result.

        Returns:
            The callee itself (enables chaining).
        """        
        self.result = result
        with open(self.result_path, "wb") as file:
            pickle.dump(self.result, file)
        return self


    def get_params(self) -> dict[str, any]:
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


    def set_initialised(self) -> Self:
        """
        Set job to initialised.

        Returns:
            The callee itself (enables chaining).
        """
        self._update_status(JobStatus.INITIALISED)
        return self


    def set_done(self, runtime: float = None) -> Self:
        """
        Set job to finished/done.

        Args:
            runtime (float | None): Optional runtime of the job. Default is None.
        Returns:
            The callee itself (enables chaining).
        """
        self._update_status(JobStatus.DONE)
        if runtime is not None:
            self.runtime = runtime
        return self


    def set_running(self) -> Self:
        """
        Set job to running.

        Returns:
            The callee itself (enables chaining).
        """
        self._update_status(JobStatus.RUNNING)
        return self


    def set_failed(self) -> Self:
        """
        Set job to failed.

        Returns:
            The callee itself (enables chaining).
        """
        self._update_status(JobStatus.FAILED)
        return self


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
        self._save()
        # with open(self.status_path, "w") as file:
        #     file.write(self.status)


    def _save(self):
        """
        Write the pickled job to file.
        """
        with open(self.pickle_path, "wb") as f:
            pickle.dump(self.__dict__, f)
    

    def _load(self):
        """
        Read the job from pickled file.
        """
        try:
            with open(self.pickle_path, "rb") as f:
                self.__dict__ = pickle.load(f)
        except Exception as e:
            raise Exception(f"Job #'{self.get_id()}' can not be read from file (pickled file does not exist).")  


    def log(self, e: Exception) -> Self:
        """
        Write to the job's log.
        
        Args:
            e (Exception): An exception object. The traceback is written to the job's log-file.
        
        Returns:
            The callee itself (enables chaining).
        """
        with open(self.log_path, "w") as file:
            traceback.print_exc(file = file)
        return self
    

    def get_log(self) -> str:
        """
        Read the job's log.

        Returns:
            The log file content as a single string.
        """
        log = ""
        with open(self.log_path, "r") as file:
            log = file.read()
        return log


    def __str__(self) -> str:
        """
        Represent job as a string.

        Returns:
            String representation of the object.
        """
        return f"#{self.id} (params: {len(self.params) - 1}, status: '{self.status}')"
