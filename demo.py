from Experiments.Registry import Registry
from Experiments.Backend import *
import random

def onemax(x: int) -> int:
    return sum(x)

def mutate(x: int, p: float) -> list[int]:
    y = x[:]
    for i in range(len(x)):
        if random.random() < p:
            y = 1 - y[i]
    return y

def ea(fun, n: int, p: float, max_n: int, opt = None) -> None:
    x: float = random.random()
    fx: int = fun(x)
    i: int = 1
    while (i <= max_n and (fx != opt)):
        y = mutate(x)
        fy = fun(y)
        if fy <= fx:
            x, fx = y, fy
        i += 1
    return fx
    
# def my_runner(jobid, params):
#     pass

def my_runner(jobid, params):
    if jobid == 1:
        raise Exception()
    #print(f"Running job #{jobid}")
    return random.uniform(1, 2)

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

print(f"No. of jobs in registry: {reg.size()}")
print(reg.get_job(400))

# Run some jobs
reg.run(my_runner, jobids = [1, 4, 6])

# Note that job 1 failed by design
print(reg.get_failed())

# Jobs 4 and 6 finished
print(reg.get_done())

# Try to run again. Jobs 4 and 6 are already finished and will thus be skipped!
reg.run(my_runner, jobids = [1, 4, 6])
print(reg.get_failed())
print(reg.get_done())

# Force jobs 4 and 6 to re-run
reg.run(my_runner, jobids = [4, 6, 10], rerun = True)
print(reg.get_failed())
print(reg.get_done())


