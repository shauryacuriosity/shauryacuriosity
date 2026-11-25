#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ -f assets/source/concept_v7b.png ]]; then
  python3 scripts/extract-rasters.py
fi
python3 scripts/build-static-svgs.py
python3 scripts/build-contributions-svg.py
python3 scripts/merge-profile-svg.py
VER="$(git rev-parse --short HEAD 2>/dev/null || echo dev)"
perl -i -pe "s|src=\"assets/profile\\.svg(\\?v=[^\"]*)?\"|src=\"assets/profile.svg?v=$VER\"|" README.md