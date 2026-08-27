#!/usr/bin/env python3
"""Write the workflow dependency versions to a JSON file.

Faithful port of upstream workflow/bgcflow/bgcflow/data/get_dependencies.py
(NBChub/bgcflow v1.1.2 @ f668687) with the env paths adapted from
workflow/envs/ to the repo-root envs/ layout. Invoked by the gated
write_dependency_versions rule (rules/branches.oxoflow); upstream's rule runs
it over project_metadata.json from the peppy-based get_project_metadata rule,
which this port does not ship (neither rule is on the upstream default path).

Usage: write_dependency_versions.py <outfile.json> <antismash_major>
"""

import json
import logging
import re
import sys

import yaml

log_format = "%(levelname)-8s %(asctime)s   %(message)s"
date_format = "%d/%m %H:%M:%S"
logging.basicConfig(format=log_format, datefmt=date_format, level=logging.DEBUG)

# list of the main dependencies used in the workflow
dependencies = {
    "antismash": r"envs/antismash.yaml",
    "bigslice": r"envs/bigslice.yaml",
    "cblaster": r"envs/cblaster.yaml",
    "prokka": r"envs/prokka.yaml",
    "eggnog-mapper": r"envs/eggnog.yaml",
    "roary": r"envs/roary.yaml",
    "seqfu": r"envs/seqfu.yaml",
    "checkm": r"envs/checkm.yaml",
    "gtdbtk": r"envs/gtdbtk.yaml",
    "gecco": r"envs/gecco.yaml",
}


def get_dependency_version(dep, dep_key, antismash_version="7"):
    """Return the dependency version tag given a dictionary (dep) and its key (dep_key)."""
    if dep_key == "antismash":
        logging.info(f"AntiSMASH version is: {antismash_version}")
        if antismash_version == "6":
            dep[dep_key] = "envs/antismash6.yaml"
    logging.info(f"Getting software version for: {dep_key}")
    with open(dep[dep_key]) as file:
        result = []
        documents = yaml.full_load(file)
        for i in documents["dependencies"]:
            if isinstance(i, str):
                # substring match: this port pins conda packages with a
                # channel prefix (e.g. bioconda::antismash=7.1.0), which
                # upstream's startswith() would miss
                if dep_key in i:
                    result = i.split("=")[-1]
            elif isinstance(i, dict):
                assert list(i.keys()) == ["pip"], i.keys()
                for p in i["pip"]:
                    if dep_key in p:
                        if p.startswith("git+"):
                            result = p.split("@")[-1]
                            if dep_key == "antismash" and "-" in result:
                                result = re.sub(r"\-", ".", result, count=2).split("-")[
                                    0
                                ]
                            else:
                                result = result.replace("-", ".")
                        else:
                            result = p.split("=")[-1]

    logging.debug(f"Version of {dep_key} is: {result}")
    return str(result)


def write_dependencies_to_json(outfile, antismash_version, dep=dependencies):
    """Write dependency versions to a JSON file."""
    with open(outfile, "w") as file:
        dv = {}
        for key in dep.keys():
            vr = get_dependency_version(dep, key, antismash_version=antismash_version)
            dv[key] = vr
        json.dump(dv, file, indent=2)
        file.close()
    return dv


if __name__ == "__main__":
    write_dependencies_to_json(sys.argv[1], sys.argv[2])
