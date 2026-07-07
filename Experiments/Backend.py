import os

from joblib import Parallel, delayed
from collections.abc import Callable

class ParallelBackend:
    def run(self, runner: Callable[[int], any], jobids: list[int]):
        pass


class JoblibBackend(ParallelBackend):
    """
    Parallelisation backend based on the joblib Python library.

    Attributes:
        ncores (int): Number of cores to use for parallelisation.
    """

    def __init__(self, ncores: int = os.cpu_count() - 1):
        """
        Initialise the Joblib backend.

        Args:
            ncores (int): ncores (int): Number of cores to use for parallelisation. Defaults to one less than the available number of cores on your machine.

        """
        self.ncores: int = ncores

    def run(self, runner: Callable[[int], any], jobids: list[int]):
        """
        Run experiments in parallel.

        Args:
            runner (Callable[[int], any]): A function that expects a job ID and returns anything. As a side effect the function shall write to the job's output path.
            jobids (list[int]): List of job IDs to be executed.

        Returns:
            A list of whatever the 'runner' function returns.
        """
        return Parallel(n_jobs = self.ncores)(delayed(runner)(jobid) for jobid in jobids)
