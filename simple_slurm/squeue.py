import os
import subprocess
import csv
from io import StringIO


class SlurmSqueueWrapper:
    def __init__(self):
        self.command = "squeue"
        self.default_format = '"%i","%j","%t","%M","%L","%D","%C","%m","%b","%R"'
        self.output_format = os.getenv("SQUEUE_FORMAT", self.default_format)

        if not self._is_valid_csv_format(self.output_format):
            raise ValueError("Invalid CSV format in SQUEUE_FORMAT environment variable")

        self.jobs = {}

    def update_squeue(self):
        """Refresh the information from the current queue for the current user"""
        result = subprocess.run(
            [self.command, "--me", "-o", self.output_format],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Error running squeue: {result.stderr}")

        self.jobs = self._parse_output(result.stdout)

    def _is_valid_csv_format(self, format_str: str):
        """validates that the output is a valid csv"""
        try:
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(format_str, delimiters=",")
            dialect.strict = True
            csv.reader(StringIO(format_str), dialect=dialect)
            return True
        except csv.Error:
            return False

    def _parse_output(self, output: str):
        """converts the stdout into a python dictionary
        each key is a jobid as integer
        """
        csv_file = StringIO(output.strip())
        reader = csv.DictReader(
            csv_file, delimiter=",", quotechar='"', skipinitialspace=True
        )
        jobs = {}
        for row in reader:
            jobs[row["JOBID"]] = row
        return jobs

    def display_jobs(self):
        """prints out all job information"""
        for job in self.jobs.values():
            print(job)

    def get_filtered_jobs(self, name_seek: str):
        """Filters jobs by name"""
        matching_jobs = {}
        for job_id, job in self.jobs.items():
            if name_seek in job["NAME"]:
                matching_jobs[job_id] = job
        return matching_jobs
