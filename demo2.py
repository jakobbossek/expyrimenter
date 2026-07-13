import random
import pandas as pd

from Experiments.Registry import Registry
from Experiments.Backend import *

# Pseudo-Boolean function OneMax 
def OneMax(x: list[int]) -> int:
    return sum(x)

# Pseudo-Boolean function LeadingOnes (short LO) 
def LO(x: list[int]) -> int:
    los = 0
    for i in x:
        if i == 0:
            return los
        los += 1
    return los

def mutate(x: list[int], p = None) -> list[int]:
    if not p:
        p = 1 / len(x)
    y = x[:]
    for i in range(len(x)):
        if random.random() < p:
            y[i] = 1 - y[i]
    return y

def ea(fun, n: int, maxevals: int) -> None:
    x: list[int] = [random.randint(0, 1) for _ in range(n)]
    fx: int = fun(x)
    nevals: int = 1
    while (nevals <= maxevals and (fx != n)):
        y = mutate(x)
        fy = fun(y)
        if fy >= fx:
            x, fx = y, fy
        nevals += 1
    return {'fx': fx, 'OPT': fx == n, 'nevals': nevals}


if __name__ == "__main__":
    # Registry folder in the file system 
    path = "expyrimenter-registry"

    # Build the registry
    reg = Registry(path = path, overwrite = True, backend = FuturesRunnerBackend())

    # Runner function.
    # Expects the job's ID and a dictionary of parameters.
    # Here the parameters are the objective function "fun" (str) and the decision space dimension "n" (int).
    # Note: jobid is not used here
    def my_runner(jobid, params):
        # Determine the target function
        fun = OneMax if (params["fun"] == "onemax") else LO
        n = int(params["n"])
        return ea(fun, n = n, maxevals = 3 * n * n)


    # Add full factorial design (2 x 3 x 10 = 60)
    fun = ["onemax", "lo"]
    n = [10, 25, 50]
    repl = list(range(1, 11))

    reg.add_jobs(fun = fun, n = n, repl = repl)
    print(f"No. of jobs in registry: {reg.size()}")

    # Run all jobs and return a "simplified" single dictionary per job
    # including the jobid, the parameters and the results.
    res = reg.run(my_runner, simplify = True)

    # Note that job 1 failed by design
    print(reg.get_failed())
    print(reg.get_done())

    print(res)
    print(pd.DataFrame(res).to_string())
    print(reg.get_job(1))


