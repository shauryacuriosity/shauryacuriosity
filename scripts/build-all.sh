#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ -f assets/source/concept_v7b.png ]]; then
  python3 scripts/extract-rasters.py
fi
python3 scripts/build-static-svgs.py
python3 scripts/build-contributions-svg.py