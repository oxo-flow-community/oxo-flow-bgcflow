#!/usr/bin/env python3
"""Convert a GenBank file to FASTA (genbank_to_fna branch).

Upstream references a scripts/genbank_to_fasta.py that does not exist
anywhere in NBChub/bgcflow @ f668687 (verified by tree enumeration), so
the port implements the evident intent with biopython's SeqIO.convert —
the same conversion bgcflow performs elsewhere on gbk inputs.
"""
import sys

from Bio import SeqIO

SeqIO.convert(sys.argv[1], "genbank", sys.argv[2], "fasta")
