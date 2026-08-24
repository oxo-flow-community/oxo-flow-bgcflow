# oxo-flow-bgcflow — Biosynthetic gene cluster (BGC) genome mining: annotation, antiSMASH and data warehouse

[![CI](https://github.com/oxo-flow-community/oxo-flow-bgcflow/actions/workflows/ci.yml/badge.svg)](https://github.com/oxo-flow-community/oxo-flow-bgcflow/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

> ★ Verified · ⇄ Official port of [`NBChub/bgcflow`](https://github.com/NBChub/bgcflow) @ `v1.1.2` — same tools, same versions, same commands. Part of the [oxo-flow-community catalog](https://oxo-flow-community.github.io/).

This workflow takes a set of your own bacterial genomes and takes them
end-to-end through biosynthetic gene cluster (BGC) discovery: prokka
annotation of every genome, antiSMASH 7 secondary-metabolite mining with
automated database setup, per-genome BGC counts and overview tables, GTDB
taxonomy lookup for each genome, download of the MIBiG reference table,
BigSCAPE-compatible comparison preparation (region symlinks, taxonomy table,
dataset registry, visualization mapping), and conversion of all result tables
into a parquet data warehouse — ready for downstream comparison, exploration,
and reporting.

## Installation

### 1. Install oxo-flow

Requires **oxo-flow >= 0.12.0**. The release binary (recommended):

```bash
curl -fL -o oxo-flow.tar.gz \
  https://github.com/Traitome/oxo-flow/releases/latest/download/oxo-flow-latest-x86_64-unknown-linux-gnu.tar.gz
tar xzf oxo-flow.tar.gz && sudo mv oxo-flow /usr/local/bin/
```

Alternatively, conda users may `conda install -c bioconda oxo-flow-cli` — note
it may lag behind releases; binaries for other platforms are on the
[releases page](https://github.com/Traitome/oxo-flow/releases).

### 2. Get this workflow

```bash
git clone https://github.com/oxo-flow-community/oxo-flow-bgcflow.git
cd oxo-flow-bgcflow
```

### 3. Requirements

**Reference data you must provide:**

- One genome FASTA per genome, `{config.raw_dir}/fasta/<genome_id>.fna`
  (`raw_dir` defaults to `test/fixtures/raw`; `.fna`/`.fasta`/`.fa` are all
  accepted) — see `config/samples.csv` for the sample table format (columns
  `genome_id,source,organism,genus,species,strain`).
- Optional: GTDB offline taxonomy TSVs (space-separated list via
  `config.gtdb_tax_paths`) if you want to skip the GTDB API/table download.

**Downloads on first run** (network access required): the antiSMASH databases
into `resources/antismash_db` (several GB), the GTDB
`bac120_metadata_r220.tsv` fallback table, and the MIBiG JSON 3.1 collection
into `resources/mibig/`.

**Compute:** up to 4 CPUs per rule (`prokka`, `antismash`); no explicit
memory limits in the workflow — antiSMASH is by far the heaviest step. Allow
several GB of disk for the downloaded resources plus the `data/` output tree.

**Tool delivery:** conda environments with pinned versions, declared in
`main.oxoflow` (`envs/antismash.yaml`, `envs/prokka.yaml`,
`envs/bgc_analytics.yaml`) — antiSMASH 7.1.0, prokka 1.14.6 and the pinned
Python analytics stack (python 3.9.18, pandas 2.0.3, pyarrow 14.0.2,
biopython 1.81, requests 2.31.0, alive_progress 3.1.5). Requires conda/mamba.

## Usage

```bash
# 1. install oxo-flow (see Installation)
# 2. prepare data: test/fixtures/raw/fasta/<genome_id>.fna + a sample table
#    (see config/samples.csv; columns genome_id,source,organism,genus,species,strain)
# 3. preview the plan
oxo-flow dry-run main.oxoflow
# 4. run
oxo-flow run main.oxoflow -j 8
# 5. run a subset
oxo-flow run main.oxoflow -t antismash --samples first:1
```

Configuration lives in the `[config]` section of `main.oxoflow`: point
`raw_dir` and `samples_csv` at your data, and tune `antismash_db_path`
(default `resources/antismash_db`), `antismash_taxon` (default `bacteria`),
and the GTDB release settings (`gtdb_release`, `gtdb_offline`). antiSMASH
requires network access on first run to download its databases.

## Source

Upstream: **[NBChub/bgcflow](https://github.com/NBChub/bgcflow)** @ `v1.1.2`
(sha `f668687aca98a7651eb0cb5a29e55286270c318d`), MIT license. Created
2026-08-15; this workflow may lag behind upstream releases. Upstream
attribution in [NOTICE.md](NOTICE.md).

## Fidelity

| Upstream rule | oxo-flow rule | Tool (version) | Notes |
|---|---|---|---|
| copy_custom_fasta | `copy_custom_fasta` | bash/coreutils | identical command |
| gtdb_prep | `gtdb_prep` | python 3.9.18, requests 2.31.0 | identical command + wget/API fallback |
| extract_meta_prokka | `extract_meta_prokka` | python 3.9.18, pandas 2.0.3 | identical command |
| prokka | `prokka` | prokka 1.14.6 | identical command; `--cpus {threads}` (4) |
| format_gbk | `format_gbk` | python 3.9.18, biopython 1.81 | identical command |
| antismash_db_setup | `antismash_db_setup` | antiSMASH 7.1.0 | v7 branch, identical command |
| antismash | `antismash` | antiSMASH 7.1.0 | v7 branch, identical command incl. reuse-result retry |
| copy_antismash | `copy_antismash` | bash/coreutils | symlink loop, identical |
| bgc_count | `bgc_count` | python 3.9.18, biopython 1.81 | identical command |
| antismash_overview | `antismash_overview` | python 3.9.18 | identical command |
| downstream_bgc_prep | `downstream_bgc_prep` | python 3.9.18, pandas 2.0.3 | identical command |
| antismash_overview_gather | `antismash_overview_gather` | python 3.9.18, pandas 2.0.3 | identical command |
| copy_log_changes | `copy_log_changes` | bash/coreutils | identical command |
| antismash_summary | `antismash_summary` | python 3.9.18, pandas 2.0.3 | identical command |
| fix_gtdb_taxonomy | `fix_gtdb_taxonomy` | python 3.9.18, pandas 2.0.3 | identical command |
| get_mibig_table | `get_mibig_table` | python 3.9.18, pandas 2.0.3 | identical command |
| copy_mibig_table | `copy_mibig_table` | bash/coreutils | identical command |
| csv_to_parquet | `csv_to_parquet` | python 3.9.18, pandas 2.0.3, pyarrow 14.0.2 | identical command |
| prokka_gbk | `prokka_gbk` | prokka 1.14.6 | `when = config.input_type == 'gbk'`; default copy_custom_fasta/prokka/format_gbk now gate on `'fna'` (upstream resolves the same producer overlap with input-function branching) |
| antismash (v6 branch) | `antismash_v6` | antiSMASH 6.x | `when = config.antismash_major == '6'`, envs/antismash6.yaml (upstream antismash_v6.yaml verbatim) |
| write_dependency_versions | `write_dependency_versions` | python | `when = config.write_dependency_versions` |
| seqfu_stats / seqfu_combine | `seqfu_stats` / `seqfu_combine` | seqfu 1.20.3 | `when = config.run_seqfu`; combine gathers via expand_inputs |
| mash / mash_convert | `mash` / `mash_convert` | mash 2.3 | `when = config.run_mash`; convert_triangular_matrix.py verbatim |
| fastani / fastani_convert | `fastani` / `fastani_convert` | fastani 1.33 | `when = config.run_fastani` |
| install_checkm / checkm / checkm_out | `install_checkm` / `checkm` | checkm-genome 1.2.2 | `when = config.run_checkm`; the 2015 CheckM DB download is the upstream install rule |
| install_gtdbtk / gtdbtk | `install_gtdbtk` / `gtdbtk` | gtdbtk 2.4.0 | `when = config.run_gtdbtk`; the release package download is multi-GB (upstream install rule) |
| prokka_db_setup / install_* rules | `install_checkm` / `install_gtdbtk` / `install_eggnog` | various | install rules for the off-by-default pipelines, same downloads as upstream |
| bigscape / copy_bigscape* | `bigscape` | bigscape (conda) | `when = config.run_bigscape`; needs the pfam + MIBiG databases in resources/ (upstream install step); the cytoscape/no-mibig variants documented in the rule header |
| bigslice / bigslice_prep / query_bigslice / fetch_bigslice_db | not ported | bigslice | `run_bigslice: true` only |
| automlst_wrapper / automlst_wrapper_out / prep_automlst_gbk | not ported | automlst | `run_automlst: true` only |
| arts + arts_extract | `arts` / `arts_extract` | arts env (upstream pins) | `when = config.run_arts`; needs the ARTS reference bundle in resources/arts; arts_extract_all.py verbatim |
| roary / roary_out | `roary` / `roary_out` | roary 3.13.0 | `when = config.run_roary`; verbatim flags (-i 80 -g 80000 -e -n -r -v) |
| install_eggnog / eggnog | `install_eggnog` / `eggnog` | eggnog-mapper 2.1.6 | `when = config.run_eggnog`; DB download + create_dbs.py as upstream |
| deeptfactor + 5 deeptfactor_* rules | not ported | deeptfactor | `run_deeptfactor: true` only |
| cblaster_genome_db | `cblaster_genome_db` | cblaster 1.3.18 | `when = config.run_cblaster`; verbatim makedb over prokka GBKs |
| gecco | `gecco` | gecco 0.9.10 | `when = config.run_gecco`; verbatim gecco run --antismash-sideload |
| amrfinderplus / amrfinder_gather | `amrfinderplus` / `amrfinder_gather` | ncbi-amrfinderplus | `when = config.run_amrfinderplus`; verbatim flags; gather_amrfinder.py verbatim |
| metabase_install / metabase_duckdb_plugin / build_warehouse | not ported | metabase/duckdb | `run_metabase: true` only |
| ncbi_genome_download + ncbi meta rules | `ncbi_genome_download` | ncbi-genome-download | `when = config.project_source == 'ncbi'`; extract_ncbi_information.py verbatim; patric stays documented (PATRIC CLI credentials/API) |
| copy_custom_genbank / genbank_to_fna | `copy_custom_genbank` / `genbank_to_fna` | python | gbk-input path (`input_type = 'gbk'`); genbank_to_fna reads the raw gbk directly (upstream uses input-function branching to avoid the producer overlap) |
| report rules (copy_readme, copy_template_notebook, mkdocs_*_report) | not ported | jupyter/mkdocs | separate `bgcflow build report` command, not in the main Snakefile |

## Test

```bash
bash test/run.sh
```

Runs `validate` + `lint` + a dry-run of the default config
(`OXO=/path/to/oxo-flow bash test/run.sh`).

## Live verification (bioinfo-wsx, oxo-flow 0.14.1, conda envs)

| Stage | Scope | Status |
|---|---|---|
| default path | S1/S2 mini fixtures: gtdb_prep, prokka, antismash v7 (+db setup), format_gbk, overview/summary, mibig table | ✅ |
| branches tier 1 | run_seqfu + run_mash + run_fastani + run_roary | ✅ (roary mini fallback — see below) |
| branches tier 2 | run_checkm (+DB install) + run_amrfinderplus (+DB install, gather) | ✅ |

Mini-fixture fallbacks (documented): roary writes a header-only
`summary_statistics.txt` plus a provenance note when the tiny synthetic
genomes yield no pangenome signal; real-data runs take the verbatim path.
Resource-gated, not live-run here: gtdbtk (r220 database ~100GB), eggnog
(20GB+), gecco/cblaster/arts/bigscape (large DBs or upstream result-layout
dependencies).

## License

Apache-2.0. Copyright (c) 2026 oxo-flow-community. Upstream (MIT) attribution
in [NOTICE.md](NOTICE.md).

## Community

https://oxo-flow-community.github.io/
