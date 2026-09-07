#!/usr/bin/env bash
# Acceptance test for oxo-flow-bgcflow port.
# Usage: ./test/run.sh            (uses ./main.oxoflow)
set -euo pipefail
cd "$(dirname "$0")/.."
OXO=${OXO:-oxo-flow}

echo "==> validate"
"$OXO" validate main.oxoflow

echo "==> lint (warnings are acceptable, errors are not)"
"$OXO" lint main.oxoflow

echo "==> dry-run with default config"
# oxo-flow v0.11.0 prints the plan to stderr; capture both streams
"$OXO" dry-run main.oxoflow --samples first:1 > /tmp/oxo-dryrun-$$.txt 2>&1
grep -q "would execute" /tmp/oxo-dryrun-$$.txt

echo "==> debug: expanded commands contain no literal {wildcards}"
"$OXO" debug main.oxoflow 2>&1 | grep -qE '\{(sample|group|config\.)' && { echo "unexpanded wildcards in debug output"; exit 1; } || true

echo "==> branch-flip: run_lsabgc=true shows the 5 lsabgc rules"
sed -e 's/^run_lsabgc = false/run_lsabgc = true/' main.oxoflow > .tmp.oxoflow
trap 'rm -f .tmp.oxoflow /tmp/oxo-dryrun-lsabgc-*.txt' EXIT
"$OXO" dry-run .tmp.oxoflow --samples first:1 > /tmp/oxo-dryrun-lsabgc-$$.txt 2>&1
for r in install_lsabgc_db lsabgc_prepare lsabgc_ready lsabgc_prepare_tax lsabgc_autoanalyze; do
    grep -qE "^  [0-9]+\. ${r}  \[run" /tmp/oxo-dryrun-lsabgc-$$.txt || { echo "lsabgc branch: expected ${r} scheduled"; exit 1; }
done
trap - EXIT
rm -f .tmp.oxoflow

echo "==> branch-flip: run_alleleome=true shows the 3 alleleome rules"
sed -e 's/^run_alleleome = false/run_alleleome = true/' main.oxoflow > .tmp.oxoflow
trap 'rm -f .tmp.oxoflow /tmp/oxo-dryrun-alleleome-*.txt' EXIT
"$OXO" dry-run .tmp.oxoflow --samples first:1 > /tmp/oxo-dryrun-alleleome-$$.txt 2>&1
for r in prepare_alleleome prepare_alleleome_fasta alleleome; do
    grep -qE "^  [0-9]+\. ${r}  \[run" /tmp/oxo-dryrun-alleleome-$$.txt || { echo "alleleome branch: expected ${r} scheduled"; exit 1; }
done
trap - EXIT
rm -f .tmp.oxoflow

echo "==> branch-flip: run_ppanggolin=true shows the ppanggolin rules"
sed -e 's/^run_ppanggolin = false/run_ppanggolin = true/' main.oxoflow > .tmp.oxoflow
trap 'rm -f .tmp.oxoflow /tmp/oxo-dryrun-ppanggolin-*.txt' EXIT
"$OXO" dry-run .tmp.oxoflow --samples first:1 > /tmp/oxo-dryrun-ppanggolin-$$.txt 2>&1
for r in ppanggolin_bgc_prep ppanggolin_BGC ppanggolin_genome ppanggolin_genome_spot_modules ppanggolin_genome_roary ppanggolin_genome_roary_spot_modules; do
    grep -qE "^  [0-9]+\. ${r}  \[run" /tmp/oxo-dryrun-ppanggolin-$$.txt || { echo "ppanggolin branch: expected ${r} scheduled"; exit 1; }
done
trap - EXIT
rm -f .tmp.oxoflow

echo "==> branch-flip: run_clinker=true shows the 5 clinker rules"
sed -e 's/^run_clinker = false/run_clinker = true/' main.oxoflow > .tmp.oxoflow
trap 'rm -f .tmp.oxoflow /tmp/oxo-dryrun-clinker-*.txt' EXIT
"$OXO" dry-run .tmp.oxoflow --samples first:1 > /tmp/oxo-dryrun-clinker-$$.txt 2>&1
for r in antismash_colourmap prep_clinker clinker_gene_functions clinker clinker_extract; do
    grep -qE "^  [0-9]+\. ${r}  \[run" /tmp/oxo-dryrun-clinker-$$.txt || { echo "clinker branch: expected ${r} scheduled"; exit 1; }
done
trap - EXIT
rm -f .tmp.oxoflow

echo "==> branch-flip: run_interproscan=true shows the 3 interproscan rules"
sed -e 's/^run_interproscan = false/run_interproscan = true/' main.oxoflow > .tmp.oxoflow
trap 'rm -f .tmp.oxoflow /tmp/oxo-dryrun-interproscan-*.txt' EXIT
"$OXO" dry-run .tmp.oxoflow --samples first:1 > /tmp/oxo-dryrun-interproscan-$$.txt 2>&1
for r in install_interproscan prepare_aa_interproscan interproscan; do
    grep -qE "^  [0-9]+\. ${r}  \[run" /tmp/oxo-dryrun-interproscan-$$.txt || { echo "interproscan branch: expected ${r} scheduled"; exit 1; }
done
trap - EXIT
rm -f .tmp.oxoflow

echo "==> branch-flip: run_mmseqs2=true shows the 9 mmseqs2 rules"
sed -e 's/^run_mmseqs2 = false/run_mmseqs2 = true/' main.oxoflow > .tmp.oxoflow
trap 'rm -f .tmp.oxoflow /tmp/oxo-dryrun-mmseqs2-*.txt' EXIT
"$OXO" dry-run .tmp.oxoflow --samples first:1 > /tmp/oxo-dryrun-mmseqs2-$$.txt 2>&1
for r in prep_gbk_mmseqs2 prepare_aa_mmseqs2 minimap2 mmseqs2_easy_cluster mmseqs2 mmseqs2_extract mmseqs2_extract_cog mmseqs2_annotate_cog mmseq_all; do
    grep -qE "^  [0-9]+\. ${r}  \[run" /tmp/oxo-dryrun-mmseqs2-$$.txt || { echo "mmseqs2 branch: expected ${r} scheduled"; exit 1; }
done
trap - EXIT
rm -f .tmp.oxoflow

echo "==> branch-flip: run_getphylo=true shows the 2 getphylo rules"
sed -e 's/^run_getphylo = false/run_getphylo = true/' main.oxoflow > .tmp.oxoflow
trap 'rm -f .tmp.oxoflow /tmp/oxo-dryrun-getphylo-*.txt' EXIT
"$OXO" dry-run .tmp.oxoflow --samples first:1 > /tmp/oxo-dryrun-getphylo-$$.txt 2>&1
for r in getphylo_prep getphylo; do
    grep -qE "^  [0-9]+\. ${r}  \[run" /tmp/oxo-dryrun-getphylo-$$.txt || { echo "getphylo branch: expected ${r} scheduled"; exit 1; }
done
trap - EXIT
rm -f .tmp.oxoflow

echo "PASS"
