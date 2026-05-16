from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


ENTRY_RE = re.compile(r"@(?P<type>[A-Za-z]+)\s*[{(]\s*(?P<key>[^,\s]+)\s*,", re.MULTILINE)


@dataclass
class Entry:
    entry_type: str
    key: str
    body: str


def split_entries(text: str) -> list[Entry]:
    matches = list(ENTRY_RE.finditer(text))
    entries: list[Entry] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        entries.append(
            Entry(
                entry_type=match.group("type"),
                key=match.group("key"),
                body=text[start:end],
            )
        )
    return entries


def get_field(body: str, field: str) -> str | None:
    pattern = re.compile(
        rf"^\s*{re.escape(field)}\s*=\s*(?P<open>[{{\"])(?P<value>.*?)(?(open)[}}\"])\s*,?\s*$",
        re.IGNORECASE | re.MULTILINE,
    )
    match = pattern.search(body)
    if not match:
        return None
    return match.group("value").strip()


def path_exists(path_text: str) -> bool:
    path = path_text.strip()
    if not path:
        return False
    return Path(path.replace("/", "\\")).exists()


def validate(bib_path: Path) -> int:
    text = bib_path.read_text(encoding="utf-8-sig")
    entries = split_entries(text)
    problems: list[str] = []
    warnings: list[str] = []

    if not entries:
        problems.append("no BibTeX entries found")

    seen_keys: set[str] = set()
    for entry in entries:
        if entry.key in seen_keys:
            problems.append(f"{entry.key}: duplicate citation key")
        seen_keys.add(entry.key)

        author = get_field(entry.body, "author")
        if author and " and " not in author and author.count(",") >= 2:
            problems.append(
                f"{entry.key}: author field looks like a comma-separated multi-author list"
            )

        pdf = get_field(entry.body, "pdf")
        file_field = get_field(entry.body, "file")

        if file_field and re.search(r"[A-Za-z]:/", file_field):
            warnings.append(
                f"{entry.key}: file field contains a drive-letter colon; prefer a pdf field for Zotero import"
            )

        if pdf:
            if "\\" in pdf:
                problems.append(f"{entry.key}: pdf path uses backslashes")
            if not path_exists(pdf):
                problems.append(f"{entry.key}: pdf path does not exist: {pdf}")
        elif file_field:
            if "\\" in file_field:
                problems.append(f"{entry.key}: file path uses backslashes")
            parts = file_field.split(":")
            candidate_path = parts[1] if len(parts) >= 3 else file_field
            if not path_exists(candidate_path):
                warnings.append(f"{entry.key}: could not confirm file path exists: {file_field}")
        else:
            warnings.append(f"{entry.key}: no pdf/file attachment field")

    print(f"Checked {len(entries)} entries in {bib_path}")
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")
    if problems:
        print("Problems:")
        for problem in problems:
            print(f"- {problem}")
        return 1
    print("BibTeX Zotero import validation passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a BibTeX file for Zotero import conventions used by paper-bib-clean."
    )
    parser.add_argument("bibfile", type=Path)
    args = parser.parse_args()
    return validate(args.bibfile)


if __name__ == "__main__":
    raise SystemExit(main())
