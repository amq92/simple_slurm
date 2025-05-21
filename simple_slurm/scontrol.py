import os
import subprocess
import csv
from io import StringIO
from pprint import pformat


class SlurmScontrolWrapper:
    def __init__(self):
        self.command = ["scontrol", "show", "job"]
        self.control = None
        self.job_id = None
        self.exit_code = None

    def __getitem__(self, key: str):
        assert self.control is not None, f"scontrol not initialized. Call 'update(<job-id>)' first"
        return [c[key] for c in self.control]

    def __len__(self):
        return len(self.control)
    
    def __iter__(self):
        assert self.control is not None, f"scontrol not initialized. Call 'update(<job-id>)' first"
        return iter(self.control)

    def __str__(self):
        assert self.control is not None, f"scontrol not initialized. Call 'update(<job-id>)' first"
        return pformat(self.control)
    
    def __repr__(self):
        return self.__str__()

    def __call__(self, job_id: str = None):
        """Get the job information for a specific job ID"""
        if job_id is not None:
            self.job_id = job_id
            self.update(job_id)
        return self

    def _get_job_id(self, job_id: str = None):
        self.job_id = job_id or self.job_id
        if self.job_id is None:
            raise ValueError("Job ID not specified. Please provide a job ID.")
        return self.job_id

    def update(self, job_id: str = None):
        """Refresh the information from the current queue for the current user"""
        job_id = self._get_job_id(job_id)
        result = subprocess.run(
            self.command + [str(job_id)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Error running scontrol: {result.stderr}")
        self.control = self._parse_output(result.stdout)
        # set exit code [0:0, 2:0]... set it to the max value. should only be 0 if ALL jobs are finished successfully
        self.exit_code = max([int(c) for e in self["ExitCode"] for c in e.split(":")])
        if self["JobState"] == "PENDING":
            self.exit_code = None

    def _parse_output(self, output: str):
        """
        Get a list of dictionaries from the scontrol output. New blocks are separated by JobId=.

        ```
        JobId=3609270 ArrayJobId=3609269 ArrayTaskId=0 JobName=test_job
        UserId=krauset(164084959) GroupId=krauset(164084959) MCS_label=N/A
        ...
        ```
        """

        def _parse_line(line):
            """Parse key=value pairs from a line of scontrol output"""
            pairs = line.strip().split()
            for pair in pairs:
                if "=" not in pair:
                    continue
                key, value = pair.split("=", 1)
                yield key, value
        
        control = []
        for i, line in enumerate(output.splitlines()):
            # start new block
            if "JobId=" in line:
                if i > 0:
                    control.append(control_i)
                control_i = {}
            # fill data
            for key, value in _parse_line(line):
                control_i[key] = value
        control.append(control_i)
        return control
