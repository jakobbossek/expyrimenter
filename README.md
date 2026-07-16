# ExPyrimenter

Lightweight Python library for **managing and executing parameterisable, inherently parallel computing jobs**.

The typical workflow is as follows:

1. Create a **registry**. The registry is the core component of the library. It manages the collection of jobs and serves as the primary interface for interacting with them.
2. Populate the registry with an **experimental design**. The design is a table in which each row defines a single job (or experiment). Each job specifies the parameters required to execute a computational task that is completely independent of the other tasks.
3. Define a **runner**. A runner is a function that accepts an integer job identifier and a dictionary of parameters. It executes the corresponding job and writes the results to the job's designated output directory.
4. Execute the jobs (in parallel) using either a built-in or custom runner backend (for example, on a multi-core local machine).
5. Monitor job progress from another Python process in read-only mode, including the number of running, completed, and failed jobs.
6. Collect and analyse the results. For benchmarking optimisation algorithms, the library provides built-in utilities for result aggregation.


## Key Features

* **Lightweight:** Focuses on the essential functionality without unnecessary complexity.
* **Extensible:** Supports multiple parallelisation backends. Currently, the library includes a simple sequential running (no parallelelisation) and an implementation based on the [joblib library](https://pypi.org/project/joblib/). Additional backends can be easily implemented.


## Installation

The package is currently under development. At a later stage it will be available via [PyPI](https://pypi.org) (the *Python Package Index*). For the time being you can use the development version.
You need *conda* to get it running easily. On MACs I suggest to use [homebrew 🍺](https://brew.sh) to install *miniconda*
```bash
brew install --cask miniconda 
```

Once done you can proceed. First, clone the repository and navigate into the respective folder in your favourite terminal application. Once there type the following to install and activate the environment:
```bash
conda env create -f environment.yml
conda activate codebase
```

## Example

```python
from Experiments.Registry import Registry
import os
import random

if __name__ == "__main__":

    # Registry folder in the file system 
    path = "expyrimenter-registry"

    # Build the registry
    reg = Registry(path = path, overwrite = True)

    # Runner function. Expects the job's ID and a dictionary of parameters.
    def my_runner(jobid, params):
        # For showcasing we force job 1 to fail 
        if jobid == 1:
            raise Exception()

        # Some arbitrary result
        return {"result": random.uniform(1, 2)}

    # Load the test design
    reg.load_design("designs/test_design.csv")

    print(reg)
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
```

## Contact

Please address questions to the main author Jakob Bossek <j.bossek@gmail.com>.
