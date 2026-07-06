from Experiments.Registry import Registry
import os
import random

path = "expregistry"

#os.removedirs(path)

def my_runner(jobid, params):
    if jobid == 1:
        raise Exception()
    #print(f"Running job #{jobid}")
    return random.uniform(1, 2)

# reg = Registry.load(path)
# print(f"No. of jobs in registry: {reg.size()}")

# print(reg.get_failed())
# print(reg.get_done())

# exit(0)

reg = Registry(path = path, overwrite = True)
reg.load_design("designs/test_design.csv")

print(f"No. of jobs in registry: {reg.size()}")
print(reg.get_job(400))
reg.run(my_runner, [1, 4, 6])
print(reg.get_failed())
print(reg.get_done())
reg.touch()
reg.run(my_runner, [1, 4, 6])
print(reg.get_failed())
print(reg.get_done())


