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

echo "PASS"
