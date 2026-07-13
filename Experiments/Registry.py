import os
import shutil
import random
import itertools

from collections.abc import Callable

from Experiments.Job import Job
from Experiments.Backend import *

class Registry:
    """
    Represents an experimental registry.

    Attributes:
        path (str): Path to registry folder in the file system.
        overwrite (bool): Shall the registry folder be overwriten if it already exists?
        locked (bool): Is a design already loaded? I.e., does the registry already contain jobs?
        job_collection (list[Job]): List of Jobs. Note that the first element is a dummy (always 'None') since jobs are numbered with natural numbers.
        n (int): Number of jobs.
        design_path (str): path to experimental design file in the registry.
        backend (RunnerBackend): Instance of a runner backend. Default is an instance of the JoblibRunnerBackend.
    """

    # Each registry holds a number of jobs starting at 1, 2, 3, ...
    njobs: int = 0 # the number of jobs

    def __init__(self, path: str, overwrite: bool = False, backend = None):
        """
        Initialise an experimental registry.

        Args:
            path (str): Path to registry folder in the file system.
            overwrite (bool): Shall the registry folder be overwriten if it already exists? Default is False.
            backend (RunnerBackend): Instance of a parallelisation backend. Default is an instance of the JoblibRunnerBackend.
        """
        self.path: str = path
        self.overwrite: bool = overwrite

        # was a design already loaded?
        self.locked: bool = False

        # list of jobs
        self.job_collection: list[int] = [None] # dummy at position 0
        self.n: int = Registry.njobs
        self.max_job_id = 1

        # path to design in registry
        self.design_path: str = os.path.join(path, "design.csv")

        # parallelisation backend
        self.backend = backend if backend is not None else JoblibRunnerBackend()

        if os.path.exists(path) and os.path.isdir(path) and not overwrite:
            print(f"Path {path} already exists and overwrite = 'False'.")
            return

        if os.path.exists(path) and overwrite:
            shutil.rmtree(path, ignore_errors = False)
            print(f"Deleted registry dir: '{self.path}'")

        # create directory
        try:
            os.makedirs(path)
        except FileExistsError:
            print(f"One or more directories in '{path}' already exist.")
        except PermissionError:
            print(f"Permission denied: Unable to create '{path}'.")
        except Exception as e:
            print(f"An error occurred in initialiser: {e}")


    def set_backend(self, backend) -> None:
        """
        Set runner backend.

        Args:
            backend (RunnerBackend): Instance of a sub-class of 'RunnerBackend'.
        """
        self.backend = backend


    @staticmethod
    def load(path: str):
        """
        Load registry from file system.

        Args:
            path (str): Path to registry folder in the file system.

        Returns:
            A registry object.
        """
        reg = Registry(path, overwrite = False)

        #  TODO: this is copy and paste
        exp_path = os.path.join(path, "design.csv")
        try:
            with open(exp_path, 'r') as f:
                # Read all rows
                rows = [x for _, x in enumerate(f)]
                
                # Split by separator
                rows = [row.strip("\n").split(',') for row in rows]

                # First line contains the 'jobid' + parameter names
                header = rows[0]

                design = rows[1:]
                for row in design:
                    jobid = int(row[0])
                    params = dict(zip(header, row))

                    reg.job_collection.append(Job(jobid, path, params))
                    reg.n += 1
                    reg.max_job_id += 1


                # Lock registry. I.e., no more jobs can be added
                reg.locked = True
            reg.touch()

        except FileNotFoundError:
            print(f"File '{path}' not found.")
        except PermissionError:
            print(f"Permission denied: Unable to read '{path}'.")
        except Exception as e:
            print(f"An error occurred: {e}")

        return reg
    
    def add_jobs(self, **kwargs) -> None:
        """
        Adds jobs via a full factorial design.

        Args:
            **kwargs (dict[str, any]): dictionary of keyword arguments.
        """
        def to_dict(l):
            # TODO: aweful implementation
            d = {}
            for x in l:
                d[x[0]] = x[1]
            return d
        
        # Extract the parameter values
        param_values = list(kwargs.values())

        # Extract the parameter names
        param_names  = list(kwargs.keys())

        # Build the experimental design (a list(dict(param_name, param_value)))
        design = [to_dict(list(zip(param_names, x))) for x in itertools.product(*(param_values))]

        # Actually add the jobs
        for params in design:
            jobid = self.max_job_id
            self.job_collection.append(Job(jobid, self.path, params))
            self.max_job_id += 1
            self.n += 1
        
        # Store the design file
        self._write_design()


    def load_design(self, path: str, sep = ",", finalise = False) -> None:
        """
        Read setup parameters from a CSV file.

        The file-format expected is a comma separated values (CSV). The first is interpreted as the header line
        with the experimental parameter names.
        Each following line contains the parameter values for one experiment.

        Args:
            path (str|path-like): Path to the design file.
            sep (str): Seperator used in the CSV-file. Default is ','.
            finalise (bool): Shall the registry be locked after execution? Default is False.
        """
        if self.locked:
            print(f"Registry is already locked with {len(self.job_collection)} jobs.")
            return

        try:
            with open(path, 'r') as f:
                # Read all rows
                rows = [x for _, x in enumerate(f)]

                # Explode by seperator
                rows = [row.strip("\n").split(sep) for row in rows]

                # The first rows entries are interpreted as the parameter names
                header = rows[0]

                design = rows[1:]
                for row in design:
                    # Sequential numbering
                    jobid = self.max_job_id

                    # Wrap parameter into a dictionary
                    params = dict(zip(header, row))

                    # Add job 
                    self.job_collection.append(Job(jobid, self.path, params))

                    # ... and ensure consistency
                    self.n += 1
                    self.max_job_id += 1

                # Lock registry. I.e., no more jobs can be added
                if finalise:
                    self.locked = True

            # copy design to internals
            self._write_design()

        except FileNotFoundError:
            print(f"File '{path}' not found.")
        except PermissionError:
            print(f"Permission denied: Unable to read '{path}'.")
        except Exception as e:
            print(f"An error occurred: {e}")


    def size(self) -> int:
        """
        Return the number of jobs.

        Returns:
            The number of jobs in the collection.
        """
        return self.n
    
    def _write_design(self):
        if self.n == 0:
            return
        
        with open(self.design_path, 'w') as f:
            param_names = ["jobid"] + self.job_collection[1].get_param_names()
            param_names_string = ",".join(param_names)
            f.write(param_names_string + "\n")

            for job in self.get_jobs():
                # Extract the job's parameter values
                param_values = list(job.get_params().values())
                jobid = job.get_id()

                # Put into one list
                row = [jobid] + param_values
                row = [str(x) for x in row]

                # Join
                row = ",".join(row)
                f.write(row + "\n")


    def _get_all_jobids(self) -> list[int]:
        """
        Return a generator of all job ids.
        """
        return range(1, self.n + 1)


    def _get_status(self, jobids: list[int] = None) -> list[str]:
        """
        Return list of statuses of jobs.

        Args:
            jobids (list[int]): list of job IDs. Default is 'None'. In this case all job IDs are considered.

        Returns:
            A list of strings.
        """
        if jobids is None:
            jobids = self._get_all_jobids()

        return [job.get_status() for job in self.get_jobs(jobids)]


    def _get_by_status(self, predicate: Callable[[Job], bool] = lambda job: True, jobids: list[int] = None) -> list[int]:
        """
        Calculate job IDs of jobs by status.

        Args:
            predicate (Callable[[Job], bool]): A function that takes a Job object and returns a Boolean.
            jobids (list[int]): An optional list of job IDs. Defaults to all job IDs.

        Returns:
            An integer list of job IDs.
        """
        filtered_jobids = [job.get_id() for job in self.get_jobs() if predicate(job)]
        if jobids is None:
            return filtered_jobids
        return list(set(filtered_jobids) & set(jobids))


    def get_failed(self, jobids: list[int] = None) -> list[int]:
        """
        Calculate job IDs of failed jobs.

        Args:
            jobids (list[int]): An optional list of job IDs. Defaults to all job IDs.

        Returns:
            An integer list of job IDs.
        """
        return self._get_by_status(lambda job: job.is_failed(), jobids)


    def get_running(self, jobids: list[int] = None) -> list[int]:
        """
        Calculate job IDs of running jobs.

        Args:
            jobids (list[int]): An optional list of job IDs. Defaults to all job IDs.

        Returns:
            An integer list of job IDs.
        """
        return self._get_by_status(lambda job: job.is_running(), jobids)


    def get_done(self, jobids: list[int] = None) -> list[int]:
        """
        Calculate job IDs of done/finished jobs.

        Args:
            jobids (list[int]): An optional list of job IDs. Defaults to all job IDs.

        Returns:
            An integer list of job IDs.
        """
        return self._get_by_status(lambda job: job.is_done(), jobids)


    def get_jobs(self, jobids: list[int] = None) -> list[Job]:
        """
        Return jobs.

        Args:
            jobids (list[int]): An optional list of job IDs. Defaults to all job IDs.

        Returns:
            A list of Job objects.
        """
        if jobids is None:
            jobids = self._get_all_jobids()
        return [self.job_collection[jobid] for jobid in jobids]


    def get_job(self, jobid: int):
        """
        Return the job with the respective ID.

        Args:
            jobid (int): The ID of the job starting at 1 (not 0).

        Returns:
            The respective 'Job' object.
        """

        # Job-IDs are 1, 2, 3, ...
        return self.job_collection[jobid]


    def touch(self) -> None:
        """
        Update job statuses.

        The function goes through all status file and reads the stored status.
        """
        jobs = self.get_jobs()
        for job in jobs:
            job.read_status()


    def run(self, runner: Callable[[int, dict[any]], bool], jobids: list = None, shuffle: bool = True, rerun: bool = False)  -> list[any]:
        """
        Run jobs in parallel.

        Args:
            runner (Callable[[int, dict(str, any), bool]]): the actual runner function. It expects exactly two parameters:
            The job ID as an int and a dictionary of algorithm parameters.
            jobids (list(int)): Optional list of job IDs. If 'None', all job IDs are used.
            shuffle (bool): Shall jobs be shuffled prior to running? Default is 'True'.
            rerun (bool): Shall finished jobs be re-run? Default is 'False', i.e., finished jobs are skipped.

        Returns:
            A list of Boolean values: 'True' if the job finished successfully and 'False' otherwise.
        """
        # If no jobs are passed, assume that all jobs are meant
        if jobids is None:
            jobids = self._get_all_jobids()

        # Shuffle jobs
        if shuffle:
            random.shuffle(jobids)

        def runner_wrapper(jobid):
            job = self.get_job(jobid)
            params = job.get_params()

            # Skip jobs if already finished
            if (job.is_done() and not rerun):
                print(f"Skipping job #{jobid} (already finished).")

            try:
                job.set_running()
                res = runner(jobid, params)
                job.set_done()
                return res
            except Exception as e:
                print(f"Job #{jobid}: An error occured (see logs for details).")
                job.log(e)
                job.set_failed()

        # Run using backend
        res = self.backend.run(runner_wrapper, jobids)

        # Update statuses
        # ToDo: for some reason they are not overwritten in the runnrer_wrapper!
        self.touch()

        return res
