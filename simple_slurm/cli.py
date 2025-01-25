import argparse

from .core import Slurm, fmt_key, read_simple_txt


def cli():
    __sbatch = "COMMAND_TO_RUN_WITH_SBATCH"

    # initialize parser
    parser = argparse.ArgumentParser(add_help=False)

    # add arguments into argparser
    arguments = read_simple_txt("arguments.txt")
    arguments_help = read_simple_txt("arguments_help.txt", False)
    for keys, help in zip(arguments, arguments_help):
        parser.add_argument(
            *(fmt_key(k) for k in keys), action=None if help else "store_true"
        )

    # add positional argument for sbatch command
    parser.add_argument(__sbatch, type=str)

    # retrieve given arguments into dict
    kwargs = vars(parser.parse_args())
    kwargs = {k: v for k, v in kwargs.items() if v is not None}

    # retrieve sbatch command and remove it from kwargs dict
    cmd = kwargs.pop(__sbatch)

    # populate the Slurm object with the provided arguments,
    # display and execute the slurm script
    slurm = Slurm(**kwargs)
    print(slurm)
    print(cmd)
    slurm.sbatch(cmd)
