<h1 align="center">Simple Slurm</h1>
<p align="center">A simple Python wrapper for Slurm with flexibility in mind<p>
<p align="center">
<a href="https://github.com/amq92/simple_slurm/actions/workflows/python-publish-pypi.yml">
    <img src="https://github.com/amq92/simple_slurm/actions/workflows/python-publish-pypi.yml/badge.svg" alt="Publish to PyPI" />
</a>
<a href="https://github.com/amq92/simple_slurm/actions/workflows/python-package-conda.yml">
    <img src="https://github.com/amq92/simple_slurm/actions/workflows/python-package-conda.yml/badge.svg" alt="Publish to Conda" />
</a>
<a href="https://github.com/amq92/simple_slurm/actions/workflows/python-run-tests.yml">
    <img src="https://github.com/amq92/simple_slurm/actions/workflows/python-run-tests.yml/badge.svg" alt="Run Python Tests" />
</a>
<a href="LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT" />
</a>
</p>

## Quickstart

```python
import datetime

from simple_slurm import Slurm

slurm = Slurm(
    array=range(3, 12),
    cpus_per_task=15,
    dependency=dict(after=65541, afterok=34987),
    gres=["gpu:kepler:2", "gpu:tesla:2", "mps:400"],
    ignore_pbs=True,
    job_name="name",
    output=f"{Slurm.JOB_ARRAY_MASTER_ID}_{Slurm.JOB_ARRAY_ID}.out",
    time=datetime.timedelta(days=1, hours=2, minutes=3, seconds=4),
)
slurm.add_cmd("module load python")
slurm.sbatch("python demo.py", Slurm.SLURM_ARRAY_TASK_ID)
```
The above snippet is equivalent to running the following command:

```bash
sbatch << EOF
#!/bin/sh

#SBATCH --array               3-11
#SBATCH --cpus-per-task       15
#SBATCH --dependency          after:65541,afterok:34987
#SBATCH --gres                gpu:kepler:2,gpu:tesla:2,mps:400
#SBATCH --ignore-pbs
#SBATCH --job-name            name
#SBATCH --output              %A_%a.out
#SBATCH --time                1-02:03:04

module load python
python demo.py \$SLURM_ARRAY_TASK_ID

EOF
```

## Installation

```bash
pip install simple_slurm
```
```bash
conda install -c conda-forge simple_slurm
```

## Contents
+ [Quickstart](#quickstart)
+ [Installation](#installation)
+ [Introduction](#introduction)
+ [Many syntaxes available](#many-syntaxes-available)
+ [Command line interface](#command-line-interface)
+ [Job dependencies](#job-dependencies)
+ [Filename Patterns and Output Environment Variables](#filename-patterns-and-output-environment-variables)
+ [Using configuration files](#using-configuration-files)
+ [`squeue` and `scancel`](#squeue-and-scancel)
+ [Error Handling](#error-handling)
+ [Contributing](#contributing)
+ [License](#contributing)
+ [Project growth](#project-growth)



## Introduction

The [`sbatch`](https://slurm.schedmd.com/sbatch.html) and [`srun`](https://slurm.schedmd.com/srun.html) commands in [Slurm](https://slurm.schedmd.com/overview.html) allow submitting parallel jobs into a Linux cluster in the form of batch scripts that follow a certain structure.

The goal of this library is to provide a simple wrapper for these functions (`sbatch` and `srun`) so that Python code can be used for constructing and launching the aforementioned batch script.

Indeed, the generated batch script can be shown by printing the `Slurm` object:

```python
from simple_slurm import Slurm

slurm = Slurm(array=range(3, 12), job_name="name")
print(slurm)
```
```bash
>> #!/bin/sh
>> 
>> #SBATCH --array               3-11
>> #SBATCH --job-name            name
```

Then, the job can be launched with either command:
```python
slurm.srun("echo hello!")
slurm.sbatch("echo hello!")
```
```bash
>> Submitted batch job 34987
```

While both commands are quite similar, [`srun`](https://slurm.schedmd.com/srun.html) will wait for the job completion, while [`sbatch`](https://slurm.schedmd.com/sbatch.html) will launch and disconnect from the jobs.
> More information can be found in [Slurm's Quick Start Guide](https://slurm.schedmd.com/quickstart.html) and in [here](https://stackoverflow.com/questions/43767866/slurm-srun-vs-sbatch-and-their-parameters).


Moreover, multi-line commands can be added using `add_cmd` and reset with `reset_cmd`.
These commands will be executed in the order they are added, and they will precede any command specified when calling `sbatch` or `srun`.

```python
slurm.add_cmd("echo hello for the first time!")
slurm.add_cmd("echo hello for the second time!")
slurm.sbatch("echo hello for the last time!")
slurm.reset_cmd()
slurm.sbatch("echo hello again!")
```
This results in two outputs
```
hello for the first time!
hello for the second time!
hello for the last time!
```
```
hello again!
```



## Many syntaxes available

```python
slurm = Slurm("-a", "3-11")
slurm = Slurm("--array", "3-11")
slurm = Slurm("array", "3-11")
slurm = Slurm(array="3-11")
slurm = Slurm(array=range(3, 12))
slurm.add_arguments(array=range(3, 12))
slurm.set_array(range(3, 12))
```

All these arguments are equivalent!
It's up to you to choose the one(s) that best suits you needs.

> *"With great flexibility comes great responsability"*

You can either keep a command-line-like syntax or a more Python-like one.

```python
slurm = Slurm()
slurm.set_dependency("after:65541,afterok:34987")
slurm.set_dependency(["after:65541", "afterok:34987"])
slurm.set_dependency(dict(after=65541, afterok=34987))
```

All the possible arguments have their own setter methods
(ex. `set_array`, `set_dependency`, `set_job_name`).

Please note that hyphenated arguments, such as `--job-name`, need to be underscored
(so to comply with Python syntax and be coherent).

```python
slurm = Slurm("--job_name", "name")
slurm = Slurm(job_name="name")

# slurm = Slurm("--job-name", "name")  # NOT VALID
# slurm = Slurm(job-name="name")       # NOT VALID
```

Moreover, boolean arguments such as `--contiguous`, `--ignore_pbs` or `--overcommit` 
can be activated with `True` or an empty string.

```python
slurm = Slurm("--contiguous", True)
slurm.add_arguments(ignore_pbs="")
slurm.set_wait(False)
print(slurm)
```
```bash
#!/bin/sh

#SBATCH --contiguous
#SBATCH --ignore-pbs
```




## Command line interface

For simpler dispatch jobs, a command line entry point is also made available.

```bash
simple_slurm [OPTIONS] "COMMAND_TO_RUN_WITH_SBATCH"
```

As such, both of these `python` and `bash` calls are equivalent.

```python
slurm = Slurm(partition="compute.p", output="slurm.log", ignore_pbs=True)
slurm.sbatch("echo \$HOSTNAME")
```
```bash
simple_slurm --partition=compute.p --output slurm.log --ignore_pbs "echo \$HOSTNAME"
```




## Job dependencies

The `sbatch` call prints a message if successful and returns the corresponding `job_id` 

```python
job_id = slurm.sbatch("python demo.py " + Slurm.SLURM_ARRAY_TAKSK_ID)
```

If the job submission was successful, it prints:

```
Submitted batch job 34987
```

And returns the variable `job_id = 34987`, which can be used for setting dependencies on subsequent jobs

```python
slurm_after = Slurm(dependency=dict(afterok=job_id)))
```


## Filename Patterns and Output Environment Variables

For convenience, Filename Patterns and Output Environment Variables are available as attributes of the Simple Slurm object.

See [https://slurm.schedmd.com/sbatch.html](https://slurm.schedmd.com/sbatch.html#lbAH) for details on the commands.

```python
from slurm import Slurm

slurm = Slurm(output=('{}_{}.out'.format(
    Slurm.JOB_ARRAY_MASTER_ID,
    Slurm.JOB_ARRAY_ID))
slurm.sbatch('python demo.py ' + slurm.SLURM_ARRAY_JOB_ID)
```

This example would result in output files of the form `65541_15.out`.
Here the job submission ID is `65541`, and this output file corresponds to the submission number `15` in the job array. Moreover, this index is passed to the Python code `demo.py` as an argument.


`sbatch` allows for a filename pattern to contain one or more replacement symbols. They can be accessed with `Slurm.<name>`

name                | value | description
:-------------------|------:|:-----------
JOB_ARRAY_MASTER_ID | %A    |  job array's master job allocation number
JOB_ARRAY_ID        | %a    |  job array id (index) number
JOB_ID_STEP_ID      | %J    |  jobid.stepid of the running job. (e.g. "128.0")
JOB_ID              | %j    |  jobid of the running job
HOSTNAME            | %N    |  short hostname. this will create a separate io file per node
NODE_IDENTIFIER     | %n    |  node identifier relative to current job (e.g. "0" is the first node of the running job) this will create a separate io file per node
STEP_ID             | %s    |  stepid of the running job
TASK_IDENTIFIER     | %t    |  task identifier (rank) relative to current job. this will create a separate io file per task
USER_NAME           | %u    |  user name
JOB_NAME            | %x    |  job name
PERCENTAGE          | %%    |  the character "%"
DO_NOT_PROCESS      | \\\\  |  do not process any of the replacement symbols



The Slurm controller will set the following variables in the environment of the batch script. They can be accessed with `Slurm.<name>`.

name                   | description
:----------------------|:-----------
SLURM_ARRAY_TASK_COUNT | total number of tasks in a job array
SLURM_ARRAY_TASK_ID    | job array id (index) number
SLURM_ARRAY_TASK_MAX   | job array's maximum id (index) number
SLURM_ARRAY_TASK_MIN   | job array's minimum id (index) number
SLURM_ARRAY_TASK_STEP  | job array's index step size
SLURM_ARRAY_JOB_ID     | job array's master job id number
...                    | ...



## Using configuration files

Let's define the *static* components of a job definition in a YAML file `slurm_default.yml`

```yaml
cpus_per_task: 15
job_name: "name"
output: "%A_%a.out"
```

Including these options with the using the `yaml` package is very *simple*

```python
import yaml

from simple_slurm import Slurm

slurm = Slurm(**yaml.load(open("slurm_default.yml", "r")))

...

slurm.set_array(range(NUMBER_OF_SIMULATIONS))
```

The job can be updated according to the *dynamic* project needs (ex. `NUMBER_OF_SIMULATIONS`).



## `squeue` and `scancel`
You can use the built-in `squeue` to retrieve information about running jobs, or even filter jobs according to their name.

```python
from simple_slurm import Slurm

slurm = Slurm(**yaml.safe_load(open("slurm_default.yml", "r")))
slurm.squeue.update_squeue()
slurm.squeue.display_jobs()
```

The `scancel` command provides two methods:

- `scancel.cancel_job()`: Sends a straightforward scancel.
- `scancel.signal_job()`: Attempts to send a SIGTERM first.

The example below cancels the first found running job from the user:

```python
from simple_slurm import Slurm

slurm = Slurm(**yaml.safe_load(open("slurm_default.yml", "r")))
slurm.squeue.update_squeue()
for job_id in slurm.squeue.jobs:
    slurm.scancel.cancel_job(job_id)
    break
```


## Error Handling
The library does not raise specific exceptions for invalid Slurm arguments or job submission failures. Instead, it relies on the underlying Slurm commands (`sbatch`, `srun`, etc.) to handle errors. If a job submission fails, the error message from Slurm will be printed to the console.

Additionally, if invalid arguments are passed to the Slurm object, the library uses `argparse` to validate them. If an argument is invalid, `argparse` will raise an error and print a helpful message.

For example:

```bash
simple_slurm --invalid_argument=value "echo \$HOSTNAME"
```

This will result in an error like:

```bash
usage: simple_slurm [OPTIONS] "COMMAND_TO_RUN_WITH_SBATCH"
simple_slurm: error: unrecognized arguments: --invalid_argument=value
```


## Contributing
Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Submit a pull request with a detailed description of your changes.



## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Project growth
[![Star History Chart](https://api.star-history.com/svg?repos=amq92/simple_slurm&type=Date)](https://star-history.com/#amq92/simple_slurm&Date)
