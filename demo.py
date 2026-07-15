import random

from Experiments.Registry import Registry
from Experiments.Backend import *

if __name__ == "__main__":

    # Registry folder in the file system 
    path = "expyrimenter-registry"

    # Build the registry
    reg = Registry(path = path, overwrite = True)#, backend = SequentialRunnerBackend())

    # Runner function.
    # Expects the job's ID and a dictionary of parameters.
    def my_runner(jobid, params):
        # For showcasing we force job 1 to fail
        if jobid == 1:
            raise Exception()

        # Some arbitrary result
        return random.uniform(1, 2)

    # Load the test design
    reg.load_design("designs/test_design.csv")
    print(reg.size())

    print(f"No. of jobs in registry: {reg.size()}")
    print(reg.get_job(400))

    # Run some jobs
    reg.run(my_runner, jobids = [1, 4, 6])

    # Note that job 1 failed by design
    print(reg.get_failed())

    # Jobs 4 and 6 finished
    print(reg.get_done())

    reg.reset_jobs([4])
    print(reg.get_done())

    # Try to run again. Jobs 4 and 6 are already finished and will thus be skipped!
    reg.run(my_runner, jobids = [1, 4, 6])
    print(reg.get_failed())
    print(reg.get_done())

    # Force jobs 4 and 6 to re-run
    reg.run(my_runner, jobids = [4, 6, 10], rerun = True)
    print(reg.get_failed())
    print(reg.get_done())
