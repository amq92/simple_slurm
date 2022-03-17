import argparse
import os
import subprocess


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
        return self.arguments()

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
        return self

    @staticmethod
    def _valid_key(key: str) -> str:
        '''Long arguments (for slurm) constructed with '-' have been internally
         represented with '_' (for Python). Correct for this in the output.
        '''
        return key.replace('_', '-')

    def arguments(self, shell: str = '/bin/sh') -> str:
        '''Generate the sbatch script for the current state of arguments.'''
        args = (
            f'#SBATCH --{self._valid_key(k):<19} {v}'
            for k, v in vars(self.namespace).items() if v is not None
        )
        script_cmd = '\n'.join((f'#!{shell}', '', *args, ''))
        return script_cmd

    def srun(self, run_cmd: str, srun_cmd: str = 'srun') -> int:
        '''Run the srun command with all the (previously) set arguments and
        the provided command to in 'run_cmd'.
        '''
        args = (
            f'--{self._valid_key(k)}={v}'
            for k, v in vars(self.namespace).items() if v is not None
        )
        cmd = ' '.join((srun_cmd, *args, run_cmd))

        result = subprocess.run(cmd, shell=True, check=True)
        return result.returncode

    def sbatch(self, run_cmd: str, convert: bool = True, verbose: bool = True,
               sbatch_cmd: str = 'sbatch', shell: str = '/bin/sh') -> int:
        '''Run the sbatch command with all the (previously) set arguments and
        the provided command to in 'run_cmd'.

        This function employs the 'here document' syntax, which requires that
        bash variables be scaped. This behavior is default, set 'convert'
        to False to disable it.

        This function employs the following syntax:
            $ slurm_cmd << EOF
            > bash_script
            > run_command
            >EOF

        For such reason if any bash variable is employed by the 'run_command',
        the '$' should be scaped into '\$'. This behavior is default, set
        'convert' to False to disable it.
        '''
        cmd = '\n'.join((
            sbatch_cmd + ' << EOF',
            self.arguments(shell),
            run_cmd.replace('$', '\\$') if convert else run_cmd,
            'EOF',
        ))
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
        success_msg = 'Submitted batch job'
        stdout = result.stdout.decode('utf-8')
        assert success_msg in stdout, result.stderr
        if verbose:
            print(stdout)
        job_id = int(stdout.split(' ')[3])
        return job_id


class Namespace:
    '''Dummy class required for accessing the arguments in argparse'''
    pass


def create_setter_method(key: str):
    '''Creates the setter method for the given 'key' attribute of a Slurm
    object
    '''

    def set_key(self, value):
        return self.add_arguments(key, value)

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
        return [[wrd.strip() for wrd in ln.split(',')] for ln in f.readlines()]
