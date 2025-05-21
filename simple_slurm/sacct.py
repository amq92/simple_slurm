import os
import subprocess
import csv
from io import StringIO
from pprint import pformat


class SlurmSacctWrapper:
    def __init__(self, fields: list = None, units: str = "M"):
        """
        Wrap and parse 'sacct'

        For example:
        sacct -j 4315805 --format=JobID,JobName%20,State,Elapsed,Start,End,NNodes,AllocCPUs,ReqCPUs,ReqMem,MaxRSS,AllocTRES --units=M

        Returns:
        JobID                     JobName      State    Elapsed               Start                 End   NNodes  AllocCPUS  ReqCPUS     ReqMem     MaxRSS  AllocTRES 
        ------------ -------------------- ---------- ---------- ------------------- ------------------- -------- ---------- -------- ---------- ---------- ---------- 
        4315805                test_slurm  COMPLETED   00:00:02 2025-04-15T13:39:11 2025-04-15T13:39:13        1          1        1      2048M            billing=1+ 
        4315805.bat+                batch  COMPLETED   00:00:02 2025-04-15T13:39:11 2025-04-15T13:39:13        1          1        1                     0 cpu=1,mem+ 
        4315805.ext+               extern  COMPLETED   00:00:02 2025-04-15T13:39:11 2025-04-15T13:39:13        1          1        1                     0 billing=1+ 

        First one is most critical. Return a list of the dictionaries (only first row). If array is submitted, they will have multiple entries.
        """
        self.fields = fields or ["JobID", "JobName", "State", "Elapsed", "Start", "End", "NNodes", "AllocCPUs", "ReqCPUs", "ReqMem", "MaxRSS"]
        self.command = ["sacct", "-j"]
        self.units = units
        self.sacct = None
        self.job_id = None
        self.exit_code = None

    def __getitem__(self, key: str):
        assert self.sacct is not None, f"sacct not initialized. Call 'update(<job-id>)' first"
        return [c[key] for c in self.sacct]

    def __len__(self):
        return len(self.sacct)
    
    def __iter__(self):
        assert self.sacct is not None, f"sacct not initialized. Call 'update(<job-id>)' first"
        return iter(self.sacct)

    def __str__(self):
        assert self.sacct is not None, f"sacct not initialized. Call 'update(<job-id>)' first"
        return pformat(self.sacct)
    
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
        self.job_id = self._get_job_id(job_id)
        result = subprocess.run(
            self.command + [str(self.job_id), f"--format={','.join(self.fields)}", f"--units={self.units}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Error running scontrol: {result.stderr}")
        self.sacct = self._parse_output(result.stdout)

    def _parse_output(self, output: str):
        """
        Get a list of dictionaries from the sacct output. New lines are detected when "JobName" is not "batch" or "extern".

        ```
        JobID                     JobName      State    Elapsed               Start                 End   NNodes  AllocCPUS  ReqCPUS     ReqMem     MaxRSS  AllocTRES 
        ------------ -------------------- ---------- ---------- ------------------- ------------------- -------- ---------- -------- ---------- ---------- ---------- 
        4319559_1                    test  COMPLETED   00:00:03 2025-04-15T13:49:15 2025-04-15T13:49:18        1          1        1      2048M            billing=1+ 
        4319559_1.b+                batch  COMPLETED   00:00:03 2025-04-15T13:49:15 2025-04-15T13:49:18        1          1        1                     0 cpu=1,mem+ 
        4319559_1.e+               extern  COMPLETED   00:00:03 2025-04-15T13:49:15 2025-04-15T13:49:18        1          1        1                     0 billing=1+ 
        4319559_2                    test  COMPLETED   00:00:03 2025-04-15T13:49:15 2025-04-15T13:49:18        1          1        1      2048M            billing=1+ 
        4319559_2.b+                batch  COMPLETED   00:00:03 2025-04-15T13:49:15 2025-04-15T13:49:18        1          1        1                     0 cpu=1,mem+ 
        4319559_2.e+               extern  COMPLETED   00:00:03 2025-04-15T13:49:15 2025-04-15T13:49:18        1          1        1                     0 billing=1+         ...
        ```
        """
        
        skip = ["batch", "extern"]
        acct = []
        for i, line in enumerate(output.splitlines()):
            # set header
            if i == 0:
                header = line.split()
                assert "JobName" in header, f"JobName not found in header: {header}. Make sure to include it in the fields."
                continue
            if i == 1:
                continue
            # add line
            acct_one = dict(zip(header, line.split()))
            if acct_one["JobName"] not in skip:
                acct.append(acct_one)

        return acct
