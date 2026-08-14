# BGCflow (port)

[![CI](https://github.com/oxo-flow-community/oxo-flow-bgcflow/actions/workflows/ci.yml/badge.svg)](https://github.com/oxo-flow-community/oxo-flow-bgcflow/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

Biosynthetic gene cluster (BGC) analysis across genomes: prokka annotation of
user-provided genomes, antiSMASH 7 secondary-metabolite mining with database
setup, BGC overview/count/summary aggregation, GTDB taxonomy lookup, MIBiG
reference table download, BigSCAPE-compatible comparison preparation
(symlinks, taxonomy, dataset registry, visualization mapping), and conversion
of all result tables into a parquet data warehouse. Ported from the Snakemake
pipeline NBChub/bgcflow default main path (`antismash: true`, all other
pipelines off).

## Source

Ported from **[NBChub/bgcflow](https://github.com/NBChub/bgcflow)**, version
`v1.1.2` (MIT). This port is maintained independently and **may lag the
upstream** — check the `v1.1.2` above and the fidelity table below for the
exact ported state.

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

## Quickstart

```bash
# 1. install oxo-flow (see Requirements)
# 2. prepare data: test/fixtures/raw/fasta/<genome_id>.fna + a sample table
#    (see config/samples.csv; columns genome_id,source,organism,genus,species,strain)
# 3. preview the plan
oxo-flow dry-run main.oxoflow
# 4. run
oxo-flow run main.oxoflow -j 8
# 5. run a subset
oxo-flow run main.oxoflow -t antismash --samples first:1
```

## Requirements

- **oxo-flow ≥ 0.11.0** — install the prebuilt binary:

```bash
curl -fL -o oxo-flow.tar.gz \
  https://github.com/Traitome/oxo-flow/releases/download/v0.11.0/oxo-flow-v0.11.0-x86_64-unknown-linux-gnu.tar.gz
tar xzf oxo-flow.tar.gz
sudo mv oxo-flow /usr/local/bin/
```

- Conda users may alternatively `conda install -c bioconda oxo-flow-cli`
  (note: the bioconda package currently lags the release binary at 0.10.2 —
  some 0.11.0 format features may not validate).
- Conda environments declared in `main.oxoflow` (`envs/antismash.yaml`,
  `envs/prokka.yaml`, `envs/bgc_analytics.yaml`) provide antiSMASH 7.1.0,
  prokka 1.14.6, and the pinned Python analytics stack. antiSMASH requires
  network access on first run to download its databases (default
  `config.antismash_db_path = "resources/antismash_db"`).

## License

Apache-2.0. Copyright (c) 2026 oxo-flow-community. Upstream attribution in
[NOTICE.md](NOTICE.md).

## Community

https://oxo-flow-community.github.io/
