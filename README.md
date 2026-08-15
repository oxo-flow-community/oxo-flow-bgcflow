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
| prokka_gbk | not ported | prokka 1.14.6 | off by default — only for genbank input files |
| antismash (v6 branch) | not ported | antiSMASH 6.x | off by default — `antismash: v6` config branch |
| write_dependency_versions | not ported | python | metadata bookkeeping, not on the default main path |
| seqfu_stats / seqfu_combine | not ported | seqfu | `run_seqfu: true` only |
| mash / mash_convert | not ported | mash | `run_mash: true` only |
| fastani / fastani_convert | not ported | fastani | `run_fastani: true` only |
| checkm / checkm_out | not ported | checkm | `run_checkm: true` only |
| gtdbtk / gtdbtk_fna_fail / evaluate_gtdbtk_input | not ported | gtdbtk | `run_gtdbtk: true` only |
| prokka_db_setup / install_* rules | not ported | various | install helpers for off-by-default pipelines |
| bigscape / bigscape_no_mibig / bigscape_to_cytoscape / copy_bigscape* | not ported | bigscape | `run_bigscape: true` only |
| bigslice / bigslice_prep / query_bigslice / fetch_bigslice_db | not ported | bigslice | `run_bigslice: true` only |
| automlst_wrapper / automlst_wrapper_out / prep_automlst_gbk | not ported | automlst | `run_automlst: true` only |
| arts + 7 arts_* rules | not ported | arts | `run_arts: true` only |
| roary / roary_reassign_pangene_categories / roary_out | not ported | roary | `run_roary: true` only |
| eggnog / eggnog_roary / eggnog_roary_result_copy | not ported | eggnog-mapper | `run_eggnog: true` only |
| deeptfactor + 5 deeptfactor_* rules | not ported | deeptfactor | `run_deeptfactor: true` only |
| cblaster_genome_db / cblaster_bgc_db | not ported | cblaster | `run_cblaster: true` only |
| gecco / gecco_aggregate / antismash_sideload_gecco | not ported | gecco | `run_gecco: true` only |
| amrfinderplus / amrfinder_gather | not ported | amrfinderplus | `run_amrfinderplus: true` only |
| metabase_install / metabase_duckdb_plugin / build_warehouse | not ported | metabase/duckdb | `run_metabase: true` only |
| ncbi_genome_download / patric_genome_download + patric/ncbi meta rules | not ported | ncbi-genome-download | non-custom genome sources |
| copy_custom_genbank / copy_converted_gbk / genbank_to_fna/gff/faa / format_genbank_meta extras | not ported | python | genbank input path, off by default |
| report rules (copy_readme, copy_template_notebook, mkdocs_*_report) | not ported | jupyter/mkdocs | separate `bgcflow build report` command, not in the main Snakefile |

## Test

```bash
bash test/run.sh
```

Runs `validate` + `lint` + a dry-run of the default config
(`OXO=/path/to/oxo-flow bash test/run.sh`).

## License

Apache-2.0. Copyright (c) 2026 oxo-flow-community. Upstream (MIT) attribution
in [NOTICE.md](NOTICE.md).

## Community

https://oxo-flow-community.github.io/
