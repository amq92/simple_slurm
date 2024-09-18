import subprocess
from loguru import logger
from datetime import datetime, timedelta

class SlurmScancelWrapper:

    sigmtems = {}
    sigmkills = {}
    stale_delta = None

    def __init__(self, staledelta = timedelta(minutes=30)):
        self.stale_delta = staledelta

    def cancel_job(self, job_id):
        '''Sends a straightforward scancel to a job'''
        result = subprocess.run(["scancel", job_id],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Error cancelling job: {result.stderr.strip()}")

    def signal_job(self, job_id):
        '''First time it is sent to a job, tries send a sigtem to the job id
        If sent again to the same job, attempts a sigkill instead
        if that fails as well, involkes scancel without term arguments
        '''
        self.prune_old_jobs()
        signal = "--signal=TERM"
        if job_id not in self.sigmtems:
            self.sigmtems[job_id] = datetime.now()
        elif job_id in self.sigmtems:
            signal = "--signal=KILL"
            self.sigmkills[job_id] = datetime.now()
            logger.warning(f"Failed to SIGTERM {job_id}. Sending SIGKILL")
        # Just straight up kills the node via slurm
        elif job_id in self.sigmtems:
            signal = ""
            logger.warning(f"Failed to SIGKILL {job_id}. Terminating!")
        result = subprocess.run(["scancel", signal, job_id],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Error cancelling job: {result.stderr.strip()}")

    def prune_old_jobs(self):
        '''Clears out signals information older than self.stale_delta'''
        for signals in [self.sigmtems, self.sigmkills]:
            for job_id in signals:
                if self.sigmtems[job_id] < datetime.now() - self.stale_delta:
                    del self.sigmtems[job_id]


    def cancel_all(self):
        '''Cancels all jobs from the current user'''
        result = subprocess.run(["scancel", "--me"],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Error cancelling job: {result.stderr.strip()}")
