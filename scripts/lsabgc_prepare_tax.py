import sys
from pathlib import Path

import pandas as pd


def lsabgc_prepare_tax(tax_csv, out_mapping):
    """
    Port of the upstream lsabgc_prepare_tax run-block (rules/lsabgc.smk).

    Reduces the project GTDB taxonomy table (df_gtdb_meta.csv) to the
    genome_id -> Organism species mapping consumed by lsaBGC-AutoAnalyze.
    """
    df = pd.read_csv(tax_csv)
    out = df.loc[:, ["genome_id", "Organism"]]
    parent = Path(out_mapping).parent
    parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_mapping, sep="\t", index=False, header=False)


if __name__ == "__main__":
    lsabgc_prepare_tax(sys.argv[1], sys.argv[2])
