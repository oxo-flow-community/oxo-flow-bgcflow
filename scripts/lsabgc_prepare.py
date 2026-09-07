import sys
from pathlib import Path

import pandas as pd


def lsabgc_prepare(mapping_csv, version, out_genbanks, out_genomes):
    """
    Port of the upstream lsabgc_prepare run-block (rules/lsabgc.smk).

    Reads the bigscape mapping CSV (bgc_id,genome_id), resolves each BGC
    region gbk under data/interim/bgcs/<project>/<version>/<genome_id>/
    and each genome fasta under data/interim/fasta/, asserts both exist,
    then writes the two lsaBGC-Ready listings:
      - <genome_id>\\t<bgc_path>            (one row per BGC region)
      - <genome_id>\\t<fna_path>            (deduplicated per genome)
    """
    mapping_path = Path(mapping_csv)
    fasta_dir = Path("data/interim/fasta")
    df = pd.read_csv(mapping_path)
    for i in df.index:
        genome_id = df.loc[i, "genome_id"]
        bgc_id = df.loc[i, "bgc_id"]
        bgc_path = mapping_path.parent / version / genome_id / (str(bgc_id) + ".gbk")
        fna_path = fasta_dir / f"{genome_id}.fna"
        df.loc[i, "bgc_path"] = str(bgc_path)
        df.loc[i, "fna_path"] = str(fna_path)
        assert bgc_path.is_file(), f"File {bgc_path} does not exist"
        assert fna_path.is_file(), f"File {fna_path} does not exist"
    out_genbanks = Path(out_genbanks)
    out_genbanks.parent.mkdir(parents=True, exist_ok=True)
    df.loc[:, ["genome_id", "bgc_path"]].to_csv(out_genbanks, sep="\t", index=False, header=False)
    df.loc[:, ["genome_id", "fna_path"]].drop_duplicates(subset=["genome_id"]).to_csv(out_genomes, sep="\t", header=False, index=False)


if __name__ == "__main__":
    lsabgc_prepare(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
