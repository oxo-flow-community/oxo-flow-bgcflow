"""Build the antismash-BGC dataset table for ppanggolin panrgp.

Port of the upstream `ppanggolin_bgc_prep` run-block
(NBChub/bgcflow v1.1.2, workflow/rules/ppanggolin.smk): walk the antismash
BGC directory, and emit a two-column TSV of <region-name>\t<region .gbk path>
for every subdirectory (skipping .snakemake internals).
"""

import sys
from pathlib import Path

import pandas as pd


def bgc_prep(bgc_dir, output_file):
    bgc = Path(bgc_dir)
    df = pd.DataFrame(
        [[i.name, str(i / f"{i.name}.gbk")] for i in bgc.glob("*") if not i.name.startswith(".snakemake")]
    )
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, sep="\t", index=False, header=False)


if __name__ == "__main__":
    bgc_prep(sys.argv[1], sys.argv[2])
