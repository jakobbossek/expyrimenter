import os
import shutil
import random

from collections.abc import Callable

from Experiments.Job import Job
from Experiments.Backend import JoblibBackend

class Registry:

    def __init__(self, path: str, overwrite: bool = False, backend = None):
        self.path = path
        self.overwrite = overwrite

        # was a design already loaded?
        self.locked = False

        # list of jobs
        self.job_collection = [None] # dummy at position 0
        self.n = 0

        # path to design in registry
        self.design_path = os.path.join(path, "design.csv")

        # parallelisation backend
        self.backend = backend if backend is not None else JoblibBackend()

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


    def set_backend(self, backend):
        self.backend = backend


    @staticmethod
    def load(path):
        reg = Registry(path, overwrite = False)

        #  TODO: this is copy and paste
        exp_path = os.path.join(path, "design.csv")
        try:
            with open(exp_path, 'r') as f:
                lines = [x for _, x in enumerate(f)]
                lines = [line.strip("\n").split(',') for line in lines]
                header = lines[0]
                design = lines[1:]
                for line in design:
                    jobid = int(line[0])
                    params = dict(zip(header, line))

                    reg.job_collection.append(Job(jobid, path, params))
                    reg.n += 1

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


    def load_design(self, path):
        '''
        Read setup parameters from file.

        job_id is the line number. Additionally the first line is read. It contains the
        parameter names. Return value is a dict with the names as keys and the string
        parameters as values.
        '''
        if self.locked:
            print(f"Registry is already locked with {len(self.job_collection)} jobs.")
            return

        try:
            with open(path, 'r') as f:
                lines = [x for _, x in enumerate(f)]
                lines = [line.strip("\n").split(',') for line in lines]
                header = lines[0]
                design = lines[1:]
                for line in design:
                    jobid = int(line[0])
                    params = dict(zip(header, line))
                    #print(params)
                    self.job_collection.append(Job(jobid, self.path, params))
                    self.n += 1

                # Lock registry. I.e., no more jobs can be added
                self.locked = True
            print("SUCCESS")

            # copy design to internals
            shutil.copyfile(path, self.design_path)
        except FileNotFoundError:
            print(f"File '{path}' not found.")
        except PermissionError:
            print(f"Permission denied: Unable to read '{path}'.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def size(self):
        """
        Return the number of jobs.

        Returns:
            The number of jobs in the collection.
        """
        return self.n

    def _get_all_jobids(self):
        return range(1, self.n + 1)

    def _get_status(self, jobids: list[int] = None):
        if jobids is None:
            jobids = self._get_all_jobids()

        return [job.get_status() for job in self.get_jobs(jobids)]

    def _get_by_status(self, predicate = lambda job: True, jobids = None):
        filtered_jobids = [job.get_id() for job in self.get_jobs() if predicate(job)]
        if jobids is None:
            return filtered_jobids
        return list(set(filtered_jobids) & set(jobids))

    def get_failed(self, jobids: list[int] = None):
        return self._get_by_status(lambda job: job.is_failed(), jobids)

    def get_running(self, jobids: list[int] = None):
        return self._get_by_status(lambda job: job.is_running(), jobids)

    def get_done(self, jobids: list[int] = None):
        return self._get_by_status(lambda job: job.is_done(), jobids)

    def get_jobs(self, jobids: list[int] = None):
        if jobids is None:
            jobids = self._get_all_jobids()
        return [self.job_collection[jobid] for jobid in jobids]

    def get_job(self, jobid):
        """
        Return the job with respective ID.

        Args:
            jobid (int): The ID of the job starting at 1 (not 0).

        Returns:
            The respective 'Job' object.
        """

        # Job-IDs are 1, 2, 3, ...
        return self.job_collection[jobid]

    def touch(self):
        jobs = self.get_jobs()
        for job in jobs:
            job.read_status()

    def run(self, runner: Callable[[int, dict[any]], bool], jobids: list = None, shuffle: bool = True, rerun: bool = False):
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
