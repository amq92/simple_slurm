import contextlib
import io
import os
import shutil
import subprocess
import sys
import unittest
from unittest.mock import patch

from simple_slurm.cli import cli


class Testing(unittest.TestCase):
    script = r"""#!/bin/sh

#SBATCH --contiguous          
#SBATCH --job-name            name
#SBATCH --time                00:01:00
""".strip()

    def test_01_using_equal(self):
        self.__run_test(
            [
                "simple_slurm",
                "--job_name=name",
                "--time=00:01:00",
                "--contiguous",
                "echo Hello!!!",
            ]
        )

    def test_02_using_spaces(self):
        self.__run_test(
            [
                "simple_slurm",
                "--job_name",
                "name",
                "--time",
                "00:01:00",
                "--contiguous",
                "echo Hello!!!",
            ]
        )

    def test_03_using_equal_and_spaces(self):
        self.__run_test(
            [
                "simple_slurm",
                "--job_name=name",
                "--time",
                "00:01:00",
                "--contiguous",
                "echo Hello!!!",
            ]
        )

    def __run_test(self, args):
        stdout = run_cli(args)
        script, job_id = parse_stdout(stdout)

        out_file = f"slurm-{job_id}.out"
        while True:  # wait for job to finalize
            if os.path.isfile(out_file):
                break
        with open(out_file, "r") as fid:
            contents = fid.read()
        os.remove(out_file)

        self.assertEqual(self.script, script)
        self.assertIn("Hello!", contents)
        self.assertIn(f"Submitted batch job {job_id}", stdout)


def run_cli(testargs):
    with io.StringIO() as buffer:
        with contextlib.redirect_stdout(buffer):
            with patch.object(sys, "argv", testargs):
                if shutil.which("sbatch") is not None:
                    cli()
                else:
                    with patch("subprocess.run", subprocess_sbatch):
                        cli()
                stdout = buffer.getvalue()
                return stdout


def subprocess_sbatch(*args, **kwargs):
    job_id = 1234
    out_file = f"slurm-{job_id}.out"
    with open(out_file, "w") as fid:
        fid.write("Hello!!!\n")
    stdout = f"Submitted batch job {job_id}"
    return subprocess.CompletedProcess(
        *args, returncode=1, stdout=stdout.encode("utf-8")
    )


def parse_stdout(stdout):
    *script, _, job_msg = stdout.strip().split("\n")
    script = "\n".join(script).strip()
    job_id = int(job_msg.replace("Submitted batch job ", ""))
    return script, job_id


if __name__ == "__main__":
    unittest.main()
