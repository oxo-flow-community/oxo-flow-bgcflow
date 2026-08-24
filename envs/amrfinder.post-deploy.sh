#!/usr/bin/env bash
# Upstream envs/amrfinderplus.post-deploy.sh, verbatim: install the
# AMRFinder database into the env (amrfinder -u). Without this the
# amrfinderplus rules die with "No valid AMRFinder database is found".
set -euo pipefail
amrfinder -u
