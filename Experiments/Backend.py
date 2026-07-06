import os

from joblib import Parallel, delayed
from collections.abc import Callable

class ParallelBackend:
    pass

class JoblibBackend(ParallelBackend):

    def __init__(self, ncores = os.cpu_count() - 1):
        self.ncores = ncores

    def run(self, runner: Callable[[int], any], jobids: list[int]):
        return Parallel(n_jobs = self.ncores)(delayed(runner)(jobid) for jobid in jobids)
