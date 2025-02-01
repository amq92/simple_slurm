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
        with io.StringIO() as buffer:
            with contextlib.redirect_stdout(buffer):
                with patch.object(sys, "argv", args):
                    cli()
                    stdout = buffer.getvalue()

        *script, _, job_msg = stdout.strip().split("\n")
        script = "\n".join(script).strip()
        job_id = int(job_msg.replace("Submitted batch job ", ""))

        self.assertEqual(self.script, script)
        self.assertIn(f"Submitted batch job {job_id}", stdout)


if __name__ == "__main__":
    unittest.main()
