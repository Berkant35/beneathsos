"""SVG → PNG with librsvg (`brew install librsvg`)."""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path


def render_png(svg_text: str, out: Path, width: int, height: int) -> Path:
    exe = shutil.which("rsvg-convert")
    if exe is None:
        raise RuntimeError("rsvg-convert not found — install librsvg (brew install librsvg)")
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False) as f:
        f.write(svg_text)
        src = f.name
    subprocess.run([exe, "-w", str(width), "-h", str(height), "-o", str(out), src], check=True)
    Path(src).unlink()
    return out
