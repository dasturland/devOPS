#!/usr/bin/env python3
"""Render UML diagram sources to PNG/SVG via the Kroki API (NFR-12).

The ``docs/diagrams/`` folder holds the source-of-truth ``.puml`` (PlantUML) and
``.mmd`` (Mermaid) files. This script POSTs each source to a Kroki server and
writes the rendered images next to the sources.

Graceful degradation: if the network / Kroki server is unreachable the script
prints a warning, leaves the source files untouched and exits ``0`` so that an
offline developer machine or a restricted CI job never fails the build.

Usage:
    python scripts/render_diagrams.py [--formats png svg] [--kroki URL]
"""

from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Map a source file extension to the Kroki diagram type.
DIAGRAM_TYPES = {
    ".puml": "plantuml",
    ".plantuml": "plantuml",
    ".mmd": "mermaid",
    ".mermaid": "mermaid",
}

DIAGRAMS_DIR = Path(__file__).resolve().parent.parent / "docs" / "diagrams"
DEFAULT_KROKI = "https://kroki.io"
DEFAULT_FORMATS = ("svg", "png")
TIMEOUT_SECONDS = 15


def render_one(source: Path, diagram_type: str, fmt: str, kroki_url: str) -> bool:
    """Render a single source file to ``fmt``. Return ``True`` on success."""
    url = f"{kroki_url.rstrip('/')}/{diagram_type}/{fmt}"
    payload = source.read_text(encoding="utf-8").encode("utf-8")
    request = urllib.request.Request(  # noqa: S310 - fixed https Kroki endpoint
        url,
        data=payload,
        headers={"Content-Type": "text/plain"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:  # noqa: S310
        data = response.read()
    target = source.with_suffix(f".{fmt}")
    target.write_bytes(data)
    print(f"  rendered {source.name} -> {target.name}")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render UML diagrams via Kroki.")
    parser.add_argument(
        "--formats",
        nargs="+",
        default=list(DEFAULT_FORMATS),
        help="Output formats (default: svg png).",
    )
    parser.add_argument(
        "--kroki",
        default=DEFAULT_KROKI,
        help=f"Kroki base URL (default: {DEFAULT_KROKI}).",
    )
    args = parser.parse_args(argv)

    if not DIAGRAMS_DIR.exists():
        print(f"warning: diagrams directory not found: {DIAGRAMS_DIR}")
        return 0

    sources = sorted(p for p in DIAGRAMS_DIR.iterdir() if p.suffix.lower() in DIAGRAM_TYPES)
    if not sources:
        print("warning: no diagram sources found; nothing to render.")
        return 0

    print(f"Rendering {len(sources)} diagram(s) via {args.kroki} ...")
    rendered = 0
    for source in sources:
        diagram_type = DIAGRAM_TYPES[source.suffix.lower()]
        for fmt in args.formats:
            try:
                if render_one(source, diagram_type, fmt, args.kroki):
                    rendered += 1
            except (urllib.error.URLError, OSError, TimeoutError) as exc:
                # Network / Kroki unreachable -> graceful degrade (NFR-12).
                print(
                    f"warning: could not render {source.name} ({fmt}): {exc}. "
                    "Leaving source intact."
                )
                print(
                    "Diagrams were not rendered (offline). Sources remain the "
                    "source of truth. Exiting cleanly."
                )
                return 0

    print(f"Done. {rendered} image(s) written to {DIAGRAMS_DIR}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
