import contextlib
import datetime
import io
import os
import shutil
import subprocess
import unittest

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
        code = slurm.srun("echo Hello!")
        self.assertEqual(code, 0)

    def test_15_sbatch_execution(self):
        slurm = Slurm(contiguous=True)
        job_id, stdout = self.__run_sbatch(slurm)

        self.assertFalse(slurm.is_parsable)
        self.assertIsInstance(job_id, int)
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

        slurm = Slurm(contiguous=True)
        job_id, stdout = self.__run_sbatch(slurm, job_file=job_file)

        self.assertFalse(slurm.is_parsable)
        self.assertIsInstance(job_id, int)
        self.assertIn(f"Submitted batch job {job_id}", stdout)

        with open(job_file, "r") as fid:
            job_contents = fid.read()
        os.remove(job_file)

        self.assertEqual(self.job_file_test_19, job_contents)

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
        slurm = Slurm(contiguous=True, parsable=True)
        job_id, stdout = self.__run_sbatch(slurm)

        self.assertTrue(slurm.is_parsable)
        self.assertIsInstance(job_id, int)
        self.assertEqual(f"{job_id}\n", stdout)

    def __run_sbatch(self, slurm, *args, **kwargs):
        with io.StringIO() as buffer:
            with contextlib.redirect_stdout(buffer):
                job_id = slurm.sbatch("echo Hello!", *args, **kwargs)
                stdout = buffer.getvalue()
        return job_id, stdout


if __name__ == "__main__":
    unittest.main()
