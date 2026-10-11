"""Regenerate all brand assets: `tools/brand/.venv/bin/python tools/brand/build.py [--app-dir DIR]`."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from brandkit.assets import build_all  # noqa: E402

HUB = Path(__file__).resolve().parents[2]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HUB / "docs" / "brand")
    parser.add_argument("--app-dir", type=Path, default=None,
                        help="also export icon/splash sources, e.g. apps/beneathsos_app/assets/branding")
    args = parser.parse_args()
    for path in build_all(args.out, args.app_dir):
        print(path.relative_to(HUB) if HUB in path.parents else path)
