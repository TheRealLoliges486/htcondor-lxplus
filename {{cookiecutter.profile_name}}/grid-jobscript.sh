#!/bin/bash
# properties = {properties}

set -e
set -x
set +u

echo "hostname:"
hostname -f
ln -s /eos/home-n/niharrin/PhD/Higgs/devel/AutoEFT2Obs/.snakemake/singularity/2899c1dcb897412d079191912bd31eca.simg
${{_CONDOR_SCRATCH_DIR}}/2899c1dcb897412d079191912bd31eca.simg

{exec_job}
