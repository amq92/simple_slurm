import argparse
import os
import subprocess
import sys


shebang = '#!/bin/sh'
sbatch_cmd = 'sbatch'


class Slurm():
    '''Simple Slurm class for running sbatch commands.

    See https://slurm.schedmd.com/sbatch.html for a complete list of arguments
    accepted by the sbatch command (ex. -a, --array).

    Validation of arguments is handled by the argparse module.

    Multiple syntaxes are allowed for defining the arguments.
    '''

    def __init__(self, *args, **kwargs):
        '''Initialize the parser with the given arguments.'''

        # initialize parser
        self.namespace = Namespace()
        self.parser = argparse.ArgumentParser()

        # add arguments into argparser
        for keys in read_simple_txt('arguments.txt'):
            self.parser.add_argument(*(fmt_key(k) for k in keys))

        # create setter methods for each argument
        for keys in read_simple_txt('arguments.txt'):
            create_setter_method(keys[0])

        # add filename patterns as static variables
        for pattern in read_simple_txt('filename_patterns.txt'):
            setattr(Slurm, *pattern)

        # add output environment variables as static variables
        for (var, ) in read_simple_txt('output_env_vars.txt'):
            setattr(Slurm, var, '$' + var)

        # add provided arguments in constructor
        self.add_arguments(*args, **kwargs)

    def __str__(self) -> str:
        '''Print the generated sbatch script.'''
        return self.arguments

    def __repr__(self) -> str:
        '''Print the argparse namespace.'''
        return repr(vars(self.namespace))

    def _add_one_argument(self, key: str, value: str):
        '''Parse the given key-value pair (the argument is given in key).

        This function handles some special cases for the type of value:
            1) A 'range' object:
                Converts range(3, 15) into '3-14'.
                Useful for defining job arrays using a Python syntax.
                Note the correct form of handling the last element.
            2) A 'dict' object:
                Converts dict(after=65541, afterok=34987)
                into 'after:65541,afterok:34987'.
                Useful for arguments that have multiple 'sub-arguments',
                such as when declaring dependencies.
        '''
        # special cases: range
        if isinstance(value, range):
            start, stop, step = value.start, value.stop - 1, value.step
            value = f'{start}-{stop}' + ('' if value.step == 1 else f':{step}')

        # special cases: dict
        if isinstance(value, dict):
            value = str(value).replace(' ', '').replace('\'', '')[1:-1]

        # add to parser
        key_value_pair = [fmt_key(key), fmt_value(value)]
        self.parser.parse_args(key_value_pair, namespace=self.namespace)

    def add_arguments(self, *args, **kwargs):
        '''Parse the given key-value pairs.

        Both syntaxes *args and **kwargs are allowed, ex:
            add_arguments('arg1', val1, 'arg2', val2, arg3=val3, arg4=val4)
        '''
        for key, value in zip(args[0::2], args[1::2]):
            self._add_one_argument(key, value)
        for key, value in kwargs.items():
            self._add_one_argument(key, value)

    @property
    def arguments(self) -> str:
        '''Generate the sbatch script for the current state of arguments.'''
        script_cmd = shebang + '\n\n'
        for key, value in vars(self.namespace).items():
            if value is not None:
                key = key.replace('_', '-')
                script_cmd += f'#SBATCH --{key:<19} {value}\n'
        return script_cmd

    def run(self, slurm_cmd: str, run_cmd: str,
            convert: bool = True, **kwargs) -> subprocess.CompletedProcess:
        '''Execute the given commands with the generated sbatch script included
        as a 'here document' code block.

        This function employs the following syntax:
            $ slurm_cmd << EOF
            > bash_script
            > run_command
            >EOF

        For such reason if any bash variable is employed by the 'run_command',
        the '$' should be scaped into '\$'. This behavior is default, set
        'convert' to False to disable it.
        '''
        return subprocess.run(
            '\n'.join([slurm_cmd + ' << EOF',
                       self.arguments,
                       run_cmd.replace('$', '\\$') if convert else run_cmd,
                       'EOF']),
            shell=True,
            **kwargs
        )

    def srun(self, run_cmd: str, convert: bool = True) -> int:
        args = (f'--{k}={v}' for (k, v) in vars(self.namespace).items() if v is not None)
        cmd = ' '.join(('srun', *args, run_cmd))

        result = subprocess.run(cmd, shell=True, check=True)
        return result.returncode

    def sbatch(self, run_cmd: str, convert: bool = True) -> int:
        '''Run the sbatch command with all the (previously) set arguments and
        the provided command to in 'run_cmd'.

        This function employs the 'here document' syntax, which requires that
        bash variables be scaped. This behavior is default, set 'convert'
        to False to disable it.

        See run for more details.
        '''
        result = self.run(sbatch_cmd, run_cmd, stdout=subprocess.PIPE)
        success_msg = 'Submitted batch job'
        stdout = result.stdout.decode('utf-8')
        assert success_msg in stdout, result.stderr
        job_id = int(stdout.replace(success_msg, ''))
        print(success_msg, job_id)
        return job_id


class Namespace:
    '''Dummy class required for accessing the arguments in argparse'''
    pass


def create_setter_method(key: str):
    '''Creates the setter method for the given 'key' attribute of a Slurm
    object
    '''
    def set_key(self, value):
        self.add_arguments(key, value)
    set_key.__name__ = f'set_{key}'
    set_key.__doc__ = f'Setter method for the argument "{key}"'
    setattr(Slurm, set_key.__name__, set_key)


def fmt_key(key: str) -> str:
    '''Maintain correct formatting for keys in key-value pairs'''
    key = str(key).strip()
    if '-' not in key:
        key = f'--{key}' if len(key) > 1 else f'-{key}'
    return key


def fmt_value(value: str) -> str:
    '''Maintain correct formatting for values in key-value pairs'''
    return str(value).strip()


def read_simple_txt(path: str) -> list:
    '''Simple function for reading the txt files.'''
    __pkg_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(__pkg_path, path), 'r') as f:
        return [[w.strip() for w in l.split(',')] for l in f.readlines()]
