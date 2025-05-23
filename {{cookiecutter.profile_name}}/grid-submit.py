#!/usr/bin/env python

import sys
import htcondor
from os import makedirs
from os.path import join, realpath
from uuid import uuid4

from snakemake.utils import read_job_properties

def fix_apptainer_args(jobscript):
  with open(jobscript, "r") as f:
    js = f.read()

  js = js.replace('--writable-tmpfs', '"--writable-tmpfs "')

  with open(jobscript, "w") as f:
    f.write(js)

jobscript = sys.argv[1]
fix_apptainer_args(jobscript)
job_properties = read_job_properties(jobscript)

UUID = uuid4()  # random UUID
jobDir = "{{cookiecutter.htcondor_log_dir}}/{}_{}".format(job_properties["jobid"], UUID)
jobDir = realpath(jobDir)
jobDir = jobDir.replace("/eos/home-", "/eos/user/")
makedirs(jobDir, exist_ok=True)

if ("/eos/user" in jobDir):
    jobDir_XRD = "root://eosuser.cern.ch/" + jobDir
elif ("/eos/cms" in jobDir):
    jobDir_XRD = "root://eoscms.cern.ch/" + jobDir
else:
    jobDir_XRD = jobDir

sub = htcondor.Submit(
    {
        "executable": "/bin/bash",
        "arguments": jobscript,
        "max_retries": "1",
        "log": join(jobDir, "condor.log"),
        "output": join(jobDir, "condor.out"),
        "error": join(jobDir, "condor.err"),
        "output_destination": jobDir_XRD,
        "getenv": "True",
        "request_cpus": str(job_properties["threads"]),
    }
)

request_memory = job_properties["resources"].get("mem_mb", None)
if request_memory is not None:
    sub["request_memory"] = str(request_memory)

request_disk = job_properties["resources"].get("disk_mb", None)
if request_disk is not None:
    sub["request_disk"] = str(request_disk)

{%- if cookiecutter.location_cern %}

# Add kerberos credentials
# c.f. https://batchdocs.web.cern.ch/local/pythonapi.html
col = htcondor.Collector()
credd = htcondor.Credd()
credd.add_user_cred(htcondor.CredTypes.Kerberos, None)
sub["MY.SendCredential"] = "True"
{%- endif %}
runtime = job_properties["resources"].get("runtime", None)
if runtime is not None:
   sub["+MaxRuntime"] = str(runtime*60) # convert minutes to seconds    

schedd = htcondor.Schedd()
clusterID = schedd.submit(sub, spool=True) # On EOS, we need to spool the jobs https://batchdocs.web.cern.ch/troubleshooting/eos.html
jobs = list(sub.jobs(clusterid=clusterID.cluster()))
schedd.spool(jobs)

# print jobid for use in Snakemake
print("{}_{}_{}".format(job_properties["jobid"], UUID, clusterID))
