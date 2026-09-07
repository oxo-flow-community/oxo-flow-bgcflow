#!/usr/bin/env python3
"""Faithful port of upstream workflow/bgcflow/bgcflow/data/get_project_metadata.py
(NBChub/bgcflow v1.1.2 @ f668687), adapted to this port's layout:

  - upstream reads config/config.yaml + workflow/rules.yaml (peppy projects,
    per-project `rules` dicts); this port has main.oxoflow + config/rules_dict.yaml
    (a verbatim copy of upstream workflow/rules.yaml), so the metadata is
    assembled from the same information without the peppy dependency.
  - the gate set mirrors upstream config.yaml `rules:` keys (the
    run_* flags in main.oxoflow): a rule is listed under `rule_used` only
    when its gate is true, exactly matching upstream's
    `for r in rules: if rules[r]` semantics.

Usage: get_project_metadata.py <project_name> <outfile.json> <bgcflow_version>
"""

import json
import logging
import sys

import yaml

log_format = "%(levelname)-8s %(asctime)s   %(message)s"
date_format = "%d/%m %H:%M:%S"
logging.basicConfig(format=log_format, datefmt=date_format, level=logging.DEBUG)

# upstream config.yaml `rules:` keys -> this port's main.oxoflow gate flags
# (upstream key name on the left, port gate on the right)
GATE_MAP = {
    "seqfu": "run_seqfu",
    "mash": "run_mash",
    "fastani": "run_fastani",
    "checkm": "run_checkm",
    "gtdbtk": "run_gtdbtk",
    "prokka-gbk": "config.input_type == 'gbk'",
    "antismash": "True",
    "query-bigslice": "run_query_bigslice",
    "bigscape": "run_bigscape",
    "bigslice": "run_bigslice",
    "automlst-wrapper": "run_automlst",
    "arts": "run_arts",
    "roary": "run_roary",
    "eggnog": "run_eggnog",
    # eggnog-roary / deeptfactor-roary are separate upstream gates whose rules
    # this port does not ship (see metadata.json excluded list) — omitting
    # them keeps rule_used faithful to what actually runs
    "deeptfactor": "run_deeptfactor",
    "cblaster-genome": "run_cblaster",
    "cblaster-bgc": "run_cblaster",
    "gecco": "run_gecco",
    "amrfinderplus": "run_amrfinderplus",
}
# upstream gates whose rules are not ported (see metadata.json excluded list)
NOT_PORTED = {"eggnog-roary", "deeptfactor-roary"}


def get_bgcflow_metadata(bgcflow_path="."):
    """Mirror upstream get_bgcflow_metadata(): read the project config and the
    rules dict (this port: main.oxoflow + config/rules_dict.yaml)."""
    import re

    bgcflow_path = bgcflow_path if bgcflow_path != "." else "."
    logging.info("Getting config metadata...")
    config = {}
    with open(f"{bgcflow_path}/main.oxoflow") as f:
        section = None
        for line in f:
            line = line.rstrip("\n")
            m = re.match(r"^\[(\w[\w.]*)\]", line)
            if m:
                section = m.group(1)
                continue
            if section != "config":
                continue
            if line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            value = value.split("#")[0].strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            config[key.strip()] = value

    logging.info("Getting rules information...")
    with open(f"{bgcflow_path}/config/rules_dict.yaml") as f:
        rules_dict = yaml.safe_load(f)

    return config, rules_dict


def get_all_metadata(config, rules_dict, bgcflow_version):
    """Mirror upstream get_all_metadata() for the single ported project."""
    logging.info("Getting metadata from projects...")
    project_metadata = {}

    name = config["project"]
    project_metadata[name] = {"description": "No description provided."}

    # get what rules are being used (upstream: for r in rules: if rules[r])
    rule_used = {}
    for r, gate in GATE_MAP.items():
        if r in NOT_PORTED:
            continue
        if r == "antismash":
            enabled = True  # antismash is TRUE on the ported default path
        elif gate.startswith("config."):
            enabled = config.get("input_type", "fna") == "gbk"
        elif gate.startswith("run_"):
            enabled = config.get(gate, "false").lower() == "true"
        else:
            enabled = False
        if enabled:
            if r in rules_dict.keys():
                rule_used[r] = rules_dict[r]
    project_metadata[name].update({"rule_used": rule_used})

    # get sample size
    import csv

    with open(config["samples_csv"]) as f:
        project_metadata[name]["sample_size"] = sum(1 for _ in csv.reader(f)) - 1

    # get citations (deduped sorted references of the used rules)
    citation_all = []
    for r in rule_used:
        citations = rule_used[r]["references"]
        citation_all.extend(citations)
    citation_all.sort()
    project_metadata[name].update({"references": citation_all})
    project_metadata[name]["references"] = list(
        set(project_metadata[name]["references"])
    )

    # get bgcflow_version
    project_metadata[name]["bgcflow_version"] = bgcflow_version
    return project_metadata


def get_project_metadata(project_name, outfile, bgcflow_version="unknown"):
    config, rules_dict = get_bgcflow_metadata()
    all_metadata = get_all_metadata(config, rules_dict, bgcflow_version)
    logging.info(f"Extracting project {project_name} metadata to {outfile}")
    with open(outfile, "w") as f:
        json.dump({project_name: all_metadata[project_name]}, f, indent=2)
    return


if __name__ == "__main__":
    get_project_metadata(sys.argv[1], sys.argv[2], bgcflow_version=sys.argv[3])
