#!/usr/bin/env python

import sys
import htcondor
from htcondor import JobEventType
from os.path import join, exists

def print_and_exit(s):
    print(s)
    exit()

jobID, UUID, clusterID = sys.argv[1].split("_")
jobDir = "{{cookiecutter.htcondor_log_dir}}/{}_{}".format(jobID, UUID)
jobLog = join(jobDir, "condor.log")

failed_states = [
    JobEventType.JOB_HELD,
    JobEventType.JOB_ABORTED,
    JobEventType.EXECUTABLE_ERROR,
]

# If the log doesn't exist yet, assume job is still running or queued
if not exists(jobLog):
    print_and_exit("running")

try:
    jel = htcondor.JobEventLog(jobLog)
    for event in jel.events(stop_after=10):
        if event.type in failed_states:
            print_and_exit("failed")
        if event.type is JobEventType.JOB_TERMINATED:
            if event.get("ReturnValue", 1) == 0:
                print_and_exit("success")
            else:
                print_and_exit("failed")
except RuntimeError as e:
    # If JobEventLog is not initialized, likely the job hasn't started writing logs
    if "JobEventLog not initialized" in str(e):
        print_and_exit("running")
    else:
        print_and_exit("failed: {}".format(e))
except Exception as e:
    print_and_exit("failed: {}".format(e))

# Default case: still running
print_and_exit("running")
