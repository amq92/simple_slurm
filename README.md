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
</p>

```python
from simple_slurm import Slurm

slurm = Slurm(
    array=range(3, 12),
    cpus_per_task=15,
    job_name='name',
    dependency=dict(after=65541, afterok=34987),
    output=f'{Slurm.JOB_ARRAY_MASTER_ID}_{Slurm.JOB_ARRAY_ID}.out',
)
slurm.sbatch('python demo.py ' + Slurm.SLURM_ARRAY_TASK_ID)
```
The above snippet is equivalent to running the following command:

```bash
sbatch << EOF
#!/bin/sh

#SBATCH --array               3-11
#SBATCH --cpus-per-task       15
#SBATCH --dependency          after:65541,afterok:34987
#SBATCH --job-name            name
#SBATCH --output              %A_%a.out

python demo.py \$SLURM_ARRAY_TASK_ID

EOF
```
See https://slurm.schedmd.com/sbatch.html for details on the commands.

> To inspect the generated script `print(slurm)` before the `sbatch` call




## Contents
+ [Installation instructions](#installation-instructions)
+ [Many syntaxes available](#many-syntaxes-available)
    - [Using configuration files](#using-configuration-files)
+ [Job dependencies](#job-dependencies)
+ [Additional features](#additional-features)
    - [Filename Patterns](#filename-patterns)
    - [Output Environment Variables](#output-environment-variables)



## Installation instructions

From PyPI

```bash
pip install simple_slurm
```

From Conda

```bash
conda install -c arturo.mendoza.quispe simple_slurm
```

From git
```bash
pip install git+https://github.com/amq92/simple_slurm.git
```



## Many syntaxes available

```python
slurm = Slurm('-a', '3-11')
slurm = Slurm('--array', '3-11')
slurm = Slurm('array', '3-11')
slurm = Slurm(array='3-11')
slurm = Slurm(array=range(3, 12))
slurm.add_arguments(array=range(3, 12))
slurm.set_array(range(3, 12))
```

All these arguments are equivalent!
It's up to you to choose the one(s) that best suits you needs.

> *"With great flexibility comes great responsability"*

You can either keep a command-line-like syntax or a more Python-like one

```python
slurm = Slurm()
slurm.set_dependency('after:65541,afterok:34987')
slurm.set_dependency(dict(after=65541, afterok=34987))
```
Each one the available arguments have their own setter method
(ex. `set_dependency`).



### Using configuration files

Let's define the *static* components of a job definition in a YAML file `default.slurm`

```yaml
cpus_per_task: 15
job_name: 'name'
output: '%A_%a.out'
```

Including these options with the using the `yaml` package is very *simple*

```python
import yaml

from simple_slurm import Slurm

slurm = Slurm(**yaml.load(open('default.slurm')))

...

slurm.set_array(range(NUMBER_OF_SIMULATIONS))
```

The job can be updated according to the *dynamic* project needs (ex. `NUMBER_OF_SIMULATIONS`).




## Job dependencies

The `sbatch` call prints a message if successful and returns the corresponding `job_id` 

```python
job_id = slurm.sbatch('python demo.py ' + Slurm.SLURM_ARRAY_TAKSK_ID)
```

If the job submission was successful, it prints:

```
Submitted batch job 34987
```

And returns the variable `job_id = 34987`, which can be used for setting dependencies on subsequent jobs

```python
slurm_after = Slurm(dependency=dict(afterok=job_id)))
```


## Additional features

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
Here the job submission ID is `65541`, and this output file corresponds to the submission number `15` in the job array. Moreover this index is passed to the Python code `demo.py` as an argument.

> Note that they can be accessed either as `Slurm.<name>` or `slurm.<name>`, here `slurm` is an instance of the `Slurm` class.



### Filename Patterns

`sbatch` allows for a filename pattern to contain one or more replacement symbols.

They can be accessed with `Slurm.<name>`

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



### Output Environment Variables

The Slurm controller will set the following variables in the environment of the batch script.

They can be accessed with `Slurm.<name>`.

name                   | description
:----------------------|:-----------
SLURM_ARRAY_TASK_COUNT | total number of tasks in a job array
SLURM_ARRAY_TASK_ID    | job array id (index) number
SLURM_ARRAY_TASK_MAX   | job array's maximum id (index) number
SLURM_ARRAY_TASK_MIN   | job array's minimum id (index) number
SLURM_ARRAY_TASK_STEP  | job array's index step size
SLURM_ARRAY_JOB_ID     | job array's master job id number
...                    | ...

See [https://slurm.schedmd.com/sbatch.html](https://slurm.schedmd.com/sbatch.html#lbAK) for a complete list.
