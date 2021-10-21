import shutil
import subprocess
import unittest
from unittest.mock import patch

from simple_slurm import Slurm


class Testing(unittest.TestCase):

    script = r'''#!/bin/sh

#SBATCH --array               3-11
#SBATCH --cpus-per-task       15
#SBATCH --dependency          after:65541,afterok:34987
#SBATCH --job-name            name
#SBATCH --output              %A_%a.out
'''

    def test_01_args_short(self):
        slurm = Slurm(
            '-a', '3-11',
            '-c', '15',
            '-J', 'name',
            '-d', 'after:65541,afterok:34987',
            '-o', r'%A_%a.out',
        )
        self.assertEqual(self.script, str(slurm))

    def test_02_args_long(self):
        slurm = Slurm(
            '--array', '3-11',
            '--cpus_per_task', '15',
            '--job_name', 'name',
            '--dependency', 'after:65541,afterok:34987',
            '--output', r'%A_%a.out',
        )
        self.assertEqual(self.script, str(slurm))

    def test_03_args_simple(self):
        slurm = Slurm(
            'array', '3-11',
            'cpus_per_task', '15',
            'job_name', 'name',
            'dependency', 'after:65541,afterok:34987',
            'output', r'%A_%a.out',
        )
        self.assertEqual(self.script, str(slurm))

    def test_04_kwargs(self):
        slurm = Slurm(
            array='3-11',
            cpus_per_task='15',
            job_name='name',
            dependency='after:65541,afterok:34987',
            output=r'%A_%a.out',
        )
        self.assertEqual(self.script, str(slurm))

    def test_05_add_arguments_single(self):
        slurm = Slurm()
        slurm.add_arguments(
            array='3-11',
            cpus_per_task='15',
            job_name='name',
            dependency='after:65541,afterok:34987',
            output=r'%A_%a.out',
        )
        self.assertEqual(self.script, str(slurm))

    def test_06_add_arguments_multiple(self):
        slurm = Slurm()
        slurm.add_arguments(array='3-11')
        slurm.add_arguments(cpus_per_task='15')
        slurm.add_arguments(job_name='name')
        slurm.add_arguments(dependency='after:65541,afterok:34987')
        slurm.add_arguments(output=r'%A_%a.out')
        self.assertEqual(self.script, str(slurm))

    def test_07_setter_methods(self):
        slurm = Slurm()
        slurm.set_array('3-11')
        slurm.set_cpus_per_task('15')
        slurm.set_job_name('name')
        slurm.set_dependency('after:65541,afterok:34987')
        slurm.set_output(r'%A_%a.out')
        self.assertEqual(self.script, str(slurm))

    def test_08_parse_range(self):
        slurm = Slurm(
            array=range(3, 12),
            cpus_per_task='15',
            job_name='name',
            dependency='after:65541,afterok:34987',
            output=r'%A_%a.out',
        )
        self.assertEqual(self.script, str(slurm))

    def test_09_parse_int(self):
        slurm = Slurm(
            array=range(3, 12),
            cpus_per_task=15,
            job_name='name',
            dependency='after:65541,afterok:34987',
            output=r'%A_%a.out',
        )
        self.assertEqual(self.script, str(slurm))

    def test_10_parse_dict(self):
        slurm = Slurm(
            array=range(3, 12),
            cpus_per_task=15,
            job_name='name',
            dependency=dict(after=65541, afterok=34987),
            output=r'%A_%a.out',
        )
        self.assertEqual(self.script, str(slurm))

    def test_11_filename_patterns(self):
        slurm = Slurm(
            array=range(3, 12),
            cpus_per_task=15,
            job_name='name',
            dependency=dict(after=65541, afterok=34987),
            output=f'{Slurm.JOB_ARRAY_MASTER_ID}_{Slurm.JOB_ARRAY_ID}.out',
        )
        self.assertEqual(self.script, str(slurm))

    def test_12_output_env_vars_object(self):
        slurm = Slurm()
        self.assertEqual(slurm.SLURM_ARRAY_TASK_ID, r'$SLURM_ARRAY_TASK_ID')

    def test_13_output_env_vars(self):
        self.assertEqual(Slurm.SLURM_ARRAY_TASK_ID, r'$SLURM_ARRAY_TASK_ID')

    def test_14_srun_returncode(self):
        slurm = Slurm()
        if shutil.which('slurm') is None:
            with patch('subprocess.run', fake_subprocess_run):
                code = slurm.srun('echo Hello!')
        else:
            code = slurm.srun('echo Hello!')
        self.assertEqual(code, 0)


def fake_subprocess_run(*args, **kwargs):
    return subprocess.CompletedProcess(*args, returncode=0)


if __name__ == '__main__':
    unittest.main()
