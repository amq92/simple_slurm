import contextlib
import datetime
import io
import os
import shutil
import subprocess
import unittest
from unittest.mock import patch

from simple_slurm import Slurm


class Testing(unittest.TestCase):
    script = r"""#!/bin/sh

#SBATCH --array               3-11
#SBATCH --cpus-per-task       15
#SBATCH --dependency          after:65541,afterok:34987
#SBATCH --gres                gpu:kepler:2,gpu:tesla:2,mps:400
#SBATCH --ignore-pbs          
#SBATCH --job-name            name
#SBATCH --output              %A_%a.out
#SBATCH --time                1-02:03:04
"""
    job_file_test_19 = r"""#!/bin/sh

#SBATCH --contiguous          

echo Hello!
"""

    commands = r"""module load python
python run.py 100
echo "done"
"""

    def test_01_args_short(self):
        slurm = Slurm(
            "-a",
            "3-11",
            "-c",
            "15",
            "-J",
            "name",
            "-d",
            "after:65541,afterok:34987",
            "-o",
            r"%A_%a.out",
            "-t",
            "1-02:03:04",
            "--gres",
            "gpu:kepler:2,gpu:tesla:2,mps:400",
            "--ignore_pbs",
            True,
        )
        self.assertEqual(self.script, str(slurm))

    def test_02_args_long(self):
        slurm = Slurm(
            "--array",
            "3-11",
            "--cpus_per_task",
            "15",
            "--job_name",
            "name",
            "--dependency",
            "after:65541,afterok:34987",
            "--output",
            r"%A_%a.out",
            "--time",
            "1-02:03:04",
            "--gres",
            "gpu:kepler:2,gpu:tesla:2,mps:400",
            "--ignore_pbs",
            True,
        )
        self.assertEqual(self.script, str(slurm))

    def test_03_args_simple(self):
        slurm = Slurm(
            "array",
            "3-11",
            "cpus_per_task",
            "15",
            "job_name",
            "name",
            "dependency",
            "after:65541,afterok:34987",
            "output",
            r"%A_%a.out",
            "time",
            "1-02:03:04",
            "gres",
            "gpu:kepler:2,gpu:tesla:2,mps:400",
            "ignore_pbs",
            True,
        )
        self.assertEqual(self.script, str(slurm))

    def test_04_kwargs(self):
        slurm = Slurm(
            array="3-11",
            cpus_per_task="15",
            job_name="name",
            dependency="after:65541,afterok:34987",
            output=r"%A_%a.out",
            time="1-02:03:04",
            gres="gpu:kepler:2,gpu:tesla:2,mps:400",
            ignore_pbs=True,
        )
        self.assertEqual(self.script, str(slurm))

    def test_05_add_arguments_single(self):
        slurm = Slurm()
        slurm.add_arguments(
            array="3-11",
            cpus_per_task="15",
            job_name="name",
            dependency="after:65541,afterok:34987",
            output=r"%A_%a.out",
            time="1-02:03:04",
            gres="gpu:kepler:2,gpu:tesla:2,mps:400",
            ignore_pbs=True,
        )
        self.assertEqual(self.script, str(slurm))

    def test_06_add_arguments_multiple(self):
        slurm = Slurm()
        slurm.add_arguments(array="3-11")
        slurm.add_arguments(cpus_per_task="15")
        slurm.add_arguments(job_name="name")
        slurm.add_arguments(dependency="after:65541,afterok:34987")
        slurm.add_arguments(output=r"%A_%a.out")
        slurm.add_arguments(time="1-02:03:04")
        slurm.add_arguments(gres="gpu:kepler:2,gpu:tesla:2,mps:400")
        slurm.add_arguments(ignore_pbs=True)
        self.assertEqual(self.script, str(slurm))

    def test_07_setter_methods(self):
        slurm = Slurm()
        slurm.set_array("3-11")
        slurm.set_cpus_per_task("15")
        slurm.set_job_name("name")
        slurm.set_dependency("after:65541,afterok:34987")
        slurm.set_output(r"%A_%a.out")
        slurm.set_time("1-02:03:04")
        slurm.set_gres("gpu:kepler:2,gpu:tesla:2,mps:400")
        slurm.set_ignore_pbs(True)
        self.assertEqual(self.script, str(slurm))

    def test_08_parse_range(self):
        slurm = Slurm(
            array=range(3, 12),
            cpus_per_task="15",
            job_name="name",
            dependency="after:65541,afterok:34987",
            output=r"%A_%a.out",
            time="1-02:03:04",
            gres="gpu:kepler:2,gpu:tesla:2,mps:400",
            ignore_pbs=True,
        )
        self.assertEqual(self.script, str(slurm))

    def test_09_parse_int(self):
        slurm = Slurm(
            array=range(3, 12),
            cpus_per_task=15,
            job_name="name",
            dependency="after:65541,afterok:34987",
            output=r"%A_%a.out",
            time="1-02:03:04",
            gres="gpu:kepler:2,gpu:tesla:2,mps:400",
            ignore_pbs=True,
        )
        self.assertEqual(self.script, str(slurm))

    def test_10_parse_dict(self):
        slurm = Slurm(
            array=range(3, 12),
            cpus_per_task=15,
            job_name="name",
            dependency=dict(after=65541, afterok=34987),
            output=r"%A_%a.out",
            time="1-02:03:04",
            gres="gpu:kepler:2,gpu:tesla:2,mps:400",
            ignore_pbs=True,
        )
        self.assertEqual(self.script, str(slurm))

    def test_11_filename_patterns(self):
        slurm = Slurm(
            array=range(3, 12),
            cpus_per_task=15,
            job_name="name",
            dependency=dict(after=65541, afterok=34987),
            output=f"{Slurm.JOB_ARRAY_MASTER_ID}_{Slurm.JOB_ARRAY_ID}.out",
            time="1-02:03:04",
            gres="gpu:kepler:2,gpu:tesla:2,mps:400",
            ignore_pbs=True,
        )
        self.assertEqual(self.script, str(slurm))

    def test_12_output_env_vars_object(self):
        slurm = Slurm()
        self.assertEqual(slurm.SLURM_ARRAY_TASK_ID, r"$SLURM_ARRAY_TASK_ID")

    def test_13_output_env_vars(self):
        self.assertEqual(Slurm.SLURM_ARRAY_TASK_ID, r"$SLURM_ARRAY_TASK_ID")

    def test_14_srun_returncode(self):
        slurm = Slurm(contiguous=True)
        if shutil.which("srun") is not None:
            code = slurm.srun("echo Hello!")
        else:
            with patch("subprocess.run", subprocess_srun):
                code = slurm.srun("echo Hello!")
        self.assertEqual(code, 0)

    def test_15_sbatch_execution(self):
        with io.StringIO() as buffer:
            with contextlib.redirect_stdout(buffer):
                slurm = Slurm(contiguous=True)
                if shutil.which("sbatch") is not None:
                    job_id = slurm.sbatch("echo Hello!")
                else:
                    with patch("subprocess.run", subprocess_sbatch):
                        job_id = slurm.sbatch("echo Hello!")
                stdout = buffer.getvalue()

        out_file = f"slurm-{job_id}.out"
        while True:  # wait for job to finalize
            if os.path.isfile(out_file):
                break
        with open(out_file, "r") as fid:
            contents = fid.read()
        os.remove(out_file)
        self.assertFalse(slurm.is_parsable)
        self.assertIsInstance(job_id, int)
        self.assertIn("Hello!", contents)
        self.assertIn(f"Submitted batch job {job_id}", stdout)

    def test_16_parse_timedelta(self):
        slurm = Slurm(
            array=range(3, 12),
            cpus_per_task=15,
            job_name="name",
            dependency=dict(after=65541, afterok=34987),
            output=r"%A_%a.out",
            time=datetime.timedelta(days=1, hours=2, minutes=3, seconds=4),
            gres="gpu:kepler:2,gpu:tesla:2,mps:400",
            ignore_pbs=True,
        )
        self.assertEqual(self.script, str(slurm))

    def test_17_parse_iterator(self):
        slurm = Slurm(
            array=[range(3, 12)],
            cpus_per_task=15,
            job_name="name",
            dependency=dict(after=65541, afterok=34987),
            output=r"%A_%a.out",
            time=datetime.timedelta(days=1, hours=2, minutes=3, seconds=4),
            gres=("gpu:kepler:2", dict(gpu=dict(tesla=2), mps=400)),
            ignore_pbs=True,
        )
        self.assertEqual(self.script, str(slurm))

    def test_18_false_boolean_arguments(self):
        slurm = Slurm(
            array=[range(3, 12)],
            cpus_per_task=15,
            job_name="name",
            dependency=dict(after=65541, afterok=34987),
            output=r"%A_%a.out",
            time=datetime.timedelta(days=1, hours=2, minutes=3, seconds=4),
            gres=("gpu:kepler:2", dict(gpu=dict(tesla=2), mps=400)),
            ignore_pbs=True,
            wait=False,
        )
        self.assertEqual(self.script, str(slurm))

    def test_19_sbatch_execution_with_job_file(self):
        job_file = "script.sh"
        with io.StringIO() as buffer:
            with contextlib.redirect_stdout(buffer):
                slurm = Slurm(contiguous=True)
                if shutil.which("sbatch") is not None:
                    job_id = slurm.sbatch("echo Hello!", job_file=job_file)
                else:
                    with patch("subprocess.run", subprocess_sbatch):
                        job_id = slurm.sbatch("echo Hello!", job_file=job_file)
                stdout = buffer.getvalue()

        self.assertIsInstance(job_id, int)

        out_file = f"slurm-{job_id}.out"
        while True:  # wait for job to finalize
            if os.path.isfile(out_file):
                break
        # Assert the script was written correctly
        with open(job_file, "r") as fid:
            job_contents = fid.read()
        os.remove(job_file)

        self.assertEqual(job_contents, self.job_file_test_19)

        # Assert the script was executed correctly
        with open(out_file, "r") as fid:
            contents = fid.read()
        os.remove(out_file)

        self.assertIn("Hello!", contents)
        self.assertIn(f"Submitted batch job {job_id}", stdout)

    def test_20_add_cmd_single(self):
        slurm = Slurm(
            "-a",
            "3-11",
            "-c",
            "15",
            "-J",
            "name",
            "-d",
            "after:65541,afterok:34987",
            "-o",
            r"%A_%a.out",
            "-t",
            "1-02:03:04",
            "--gres",
            "gpu:kepler:2,gpu:tesla:2,mps:400",
            "--ignore_pbs",
            True,
        )
        slurm.add_cmd(
            "\n".join(
                (
                    "module load python",
                    "python run.py 100",
                    'echo "done"',
                )
            )
        )
        self.assertEqual(self.script + "\n" + self.commands, str(slurm))

    def test_21_add_cmd_multiple(self):
        slurm = Slurm(
            "-a",
            "3-11",
            "-c",
            "15",
            "-J",
            "name",
            "-d",
            "after:65541,afterok:34987",
            "-o",
            r"%A_%a.out",
            "-t",
            "1-02:03:04",
            "--gres",
            "gpu:kepler:2,gpu:tesla:2,mps:400",
            "--ignore_pbs",
            True,
        )
        slurm.add_cmd("module load python")
        slurm.add_cmd("python run.py 100")
        slurm.add_cmd('echo "done"')
        self.assertEqual(self.script + "\n" + self.commands, str(slurm))

    def test_22_parsable_sbatch_execution(self):
        with io.StringIO() as buffer:
            with contextlib.redirect_stdout(buffer):
                slurm = Slurm(contiguous=True, parsable=True)
                if shutil.which("sbatch") is not None:
                    job_id = slurm.sbatch("echo Hello!")
                else:
                    with patch("subprocess.run", subprocess_sbatch_parsable):
                        job_id = slurm.sbatch("echo Hello!")
                stdout = buffer.getvalue()

        out_file = f"slurm-{job_id}.out"
        while True:  # wait for job to finalize
            if os.path.isfile(out_file):
                break
        with open(out_file, "r") as fid:
            contents = fid.read()
        os.remove(out_file)
        self.assertTrue(slurm.is_parsable)
        self.assertIsInstance(job_id, int)
        self.assertIn("Hello!", contents)
        self.assertEqual(f"{job_id}\n", stdout)


def subprocess_srun(*args, **kwargs):
    print("Hello!!!")
    return subprocess.CompletedProcess(*args, returncode=0)


def subprocess_sbatch(*args, **kwargs):
    job_id = 1234
    out_file = f"slurm-{job_id}.out"
    with open(out_file, "w") as fid:
        fid.write("Hello!!!\n")
    stdout = f"Submitted batch job {job_id}"
    return subprocess.CompletedProcess(
        *args, returncode=1, stdout=stdout.encode("utf-8")
    )


def subprocess_sbatch_parsable(*args, **kwargs):
    job_id = 1234
    out_file = f"slurm-{job_id}.out"
    with open(out_file, "w") as fid:
        fid.write("Hello!!!\n")
    stdout = str(job_id)
    return subprocess.CompletedProcess(
        *args, returncode=0, stdout=stdout.encode("utf-8")
    )


if __name__ == "__main__":
    unittest.main()
