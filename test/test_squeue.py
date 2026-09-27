import unittest

from simple_slurm.squeue import SlurmSqueueWrapper


class TestSqueueParsing(unittest.TestCase):
    output = """"JOBID","NAME","ST","TIME","TIME_LEFT","NODES","CPUS","MIN_MEMORY","TRES_PER_NODE","NODELIST(REASON)"
"662099","plain","R","1:02","58:58","1","1","4G","N/A","node01"
"662100_351","array","R","0:10","59:50","1","1","4G","N/A","node02"
"662100_[352-467%256]","array","PD","0:00","1:00:00","1","1","4G","N/A","(JobArrayTaskLimit)"
"""

    def test_parse_output_with_job_arrays(self):
        jobs = SlurmSqueueWrapper()._parse_output(self.output)
        self.assertEqual(list(jobs), [662099, "662100_351", "662100_[352-467%256]"])
        self.assertEqual(jobs[662099]["NAME"], "plain")
        self.assertEqual(jobs["662100_[352-467%256]"]["ST"], "PD")


if __name__ == "__main__":
    unittest.main()
