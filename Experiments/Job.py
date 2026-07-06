import os
import traceback

class Job:

    def __init__(self, id: int, path: str, params: dict):
        self.id = id
        self.params = params
        self.status = "INITIALISED"
        self.output_path = os.path.join(path, "experiments", str(id))
        self.status_path = os.path.join(path, "experiments", str(id), "status.txt")
        self.log_path    = os.path.join(path, "experiments", str(id), "log.txt")
        self.create_paths()

    def create_paths(self):
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
            with open(self.status_path, "w") as file:
                file.write(self.status)
            with open(self.log_path, "w") as file:
                file.write("")

    def get_outout_path(self):
        return self.output_path

    def get_id(self):
        return self.id

    def get_params(self):
        return self.params

    def get_status(self):
        return self.status

    def set_done(self):
        self._update_status("DONE")

    def set_running(self):
        self._update_status("RUNNING")

    def set_failed(self):
        self._update_status("FAILED")

    def is_done(self):
        return self.status == "DONE"

    def is_failed(self):
        return self.status == "FAILED"

    def is_running(self):
        return self.status == "RUNNING"

    def is_initialised(self):
        return self.status == "INITIALISED"

    def _update_status(self, status: str):
        self.status = status
        with open(self.status_path, "w") as file:
            file.write(self.status)

    def read_status(self):
        with open(self.status_path, "r") as file:
            self.status = file.read()


    def log(self, e: Exception):
        with open(self.log_path, "w") as file:
            traceback.print_exc(file = file)

    def __str__(self):
        return f"#{self.id} (params: {len(self.params) - 1}, status: '{self.status}')"
