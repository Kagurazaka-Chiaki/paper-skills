#!/usr/bin/env python3
"""Collect lightweight matching signals from a PDF using optional local tools."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


def run_tool(args: list[str]) -> str | None:
    try:
        result = subprocess.run(
            args,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: collect_signals.py <paper.pdf>", file=sys.stderr)
        return 2

    pdf_path = Path(sys.argv[1]).resolve()
    payload: dict[str, object] = {
        "pdf_path": str(pdf_path),
        "pdfinfo_available": shutil.which("pdfinfo") is not None,
        "pdftotext_available": shutil.which("pdftotext") is not None,
        "pdfinfo": None,
        "first_page_text": None,
    }

    if shutil.which("pdfinfo"):
        payload["pdfinfo"] = run_tool(["pdfinfo", str(pdf_path)])

    if shutil.which("pdftotext"):
        payload["first_page_text"] = run_tool(
            ["pdftotext", "-f", "1", "-l", "1", "-nopgbrk", "-layout", str(pdf_path), "-"]
        )

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
