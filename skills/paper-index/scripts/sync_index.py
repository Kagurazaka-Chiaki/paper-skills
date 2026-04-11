from __future__ import annotations

import argparse
import ast
import json
import re
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class PaperRecord:
    bibkey: str
    title: str
    author: str
    year: int | None
    venue: str
    doi: str
    area: str
    status: str
    note_path: str
    pdf_path: str
    short_title_zh: str
    tags_json: str


def parse_frontmatter(note_path: Path) -> dict[str, object]:
    text = note_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        return {}
    frontmatter: dict[str, object] = {}
    i = 1
    while i < len(lines):
        line = lines[i]
        if line.strip() == "---":
            break
        if ":" not in line:
            i += 1
            continue
        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if value.startswith("[") and value.endswith("]"):
            try:
                parsed = ast.literal_eval(value)
            except Exception:
                parsed = [item.strip() for item in value[1:-1].split(",") if item.strip()]
            frontmatter[key] = parsed
        elif re.fullmatch(r"-?\d+", value):
            frontmatter[key] = int(value)
        else:
            frontmatter[key] = value
        i += 1
    return frontmatter


def extract_title(note_path: Path) -> str:
    text = note_path.read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return note_path.stem


def normalize_rel_path(value: object) -> str:
    if not isinstance(value, str):
        return ""
    normalized = value.replace("\\", "/").strip()
    while normalized.startswith("../"):
        normalized = normalized[3:]
    return normalized


def load_records(workspace_root: Path) -> list[PaperRecord]:
    notes_dir = workspace_root / "07-Resources" / "Papers"
    records: list[PaperRecord] = []
    for note_path in sorted(notes_dir.glob("*.md")):
        if note_path.name.lower() == "readme.md":
            continue
        frontmatter = parse_frontmatter(note_path)
        if frontmatter.get("type") != "paper":
            continue
        bibkey = str(frontmatter.get("bibkey", "")).strip()
        if not bibkey:
            continue
        tags = frontmatter.get("tags", [])
        if isinstance(tags, list):
            tags_json = json.dumps(tags, ensure_ascii=False)
        else:
            tags_json = json.dumps([])
        records.append(
            PaperRecord(
                bibkey=bibkey,
                title=extract_title(note_path),
                author=str(frontmatter.get("author", "")).strip(),
                year=frontmatter.get("year") if isinstance(frontmatter.get("year"), int) else None,
                venue=str(frontmatter.get("venue", "")).strip(),
                doi=str(frontmatter.get("doi", "")).strip(),
                area=str(frontmatter.get("area", "")).strip(),
                status=str(frontmatter.get("status", "")).strip(),
                note_path=str(note_path.relative_to(workspace_root)).replace("\\", "/"),
                pdf_path=normalize_rel_path(frontmatter.get("source", "")),
                short_title_zh=str(frontmatter.get("short_title_zh", "")).strip(),
                tags_json=tags_json,
            )
        )
    return records


def write_sqlite(db_path: Path, records: list[PaperRecord]) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS papers (
                bibkey TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT,
                year INTEGER,
                venue TEXT,
                doi TEXT,
                area TEXT,
                status TEXT,
                note_path TEXT NOT NULL,
                pdf_path TEXT NOT NULL,
                short_title_zh TEXT,
                tags_json TEXT NOT NULL DEFAULT '[]',
                updated_at TEXT NOT NULL
            )
            """
        )
        existing_keys = {
            row[0] for row in conn.execute("SELECT bibkey FROM papers")
        }
        incoming_keys = {record.bibkey for record in records}
        stale_keys = existing_keys - incoming_keys
        if stale_keys:
            conn.executemany("DELETE FROM papers WHERE bibkey = ?", [(key,) for key in stale_keys])
        now = datetime.now(timezone.utc).isoformat()
        conn.executemany(
            """
            INSERT INTO papers (
                bibkey, title, author, year, venue, doi, area, status, note_path, pdf_path,
                short_title_zh, tags_json, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(bibkey) DO UPDATE SET
                title=excluded.title,
                author=excluded.author,
                year=excluded.year,
                venue=excluded.venue,
                doi=excluded.doi,
                area=excluded.area,
                status=excluded.status,
                note_path=excluded.note_path,
                pdf_path=excluded.pdf_path,
                short_title_zh=excluded.short_title_zh,
                tags_json=excluded.tags_json,
                updated_at=excluded.updated_at
            """,
            [
                (
                    record.bibkey,
                    record.title,
                    record.author,
                    record.year,
                    record.venue,
                    record.doi,
                    record.area,
                    record.status,
                    record.note_path,
                    record.pdf_path,
                    record.short_title_zh,
                    record.tags_json,
                    now,
                )
                for record in records
            ],
        )
        conn.commit()
    finally:
        conn.close()


def bib_type_for(record: PaperRecord) -> str:
    if "neurips" in record.venue.lower() or "siggraph" in record.venue.lower() or "iclr" in record.venue.lower():
        return "inproceedings"
    if "journal" in record.venue.lower() or "forum" in record.venue.lower():
        return "article"
    return "misc"


def bib_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")


def write_bib(bib_path: Path, records: list[PaperRecord]) -> None:
    bib_path.parent.mkdir(parents=True, exist_ok=True)
    chunks: list[str] = []
    for record in records:
        fields: list[tuple[str, str]] = [
            ("author", record.author),
            ("title", record.title),
        ]
        if record.year is not None:
            fields.append(("year", str(record.year)))
        if record.venue:
            key = "journal" if bib_type_for(record) == "article" else "booktitle" if bib_type_for(record) == "inproceedings" else "note"
            fields.append((key, record.venue))
        elif record.area:
            fields.append(("keywords", record.area))
        if record.area and record.venue:
            fields.append(("keywords", record.area))
        if record.doi:
            fields.append(("doi", record.doi))
        rendered = ",\n".join(f"  {key} = {{{bib_escape(value)}}}" for key, value in fields if value)
        chunks.append(f"@{bib_type_for(record)}{{{record.bibkey},\n{rendered}\n}}")
    bib_path.write_text("\n\n".join(chunks) + ("\n" if chunks else ""), encoding="utf-8")


def stem_for_rel_path(path_str: str) -> str:
    if not path_str:
        return ""
    return Path(path_str.replace("\\", "/")).stem


def collect_basename_mismatches(records: list[PaperRecord]) -> list[str]:
    mismatches: list[str] = []
    for record in records:
        note_stem = stem_for_rel_path(record.note_path)
        pdf_stem = stem_for_rel_path(record.pdf_path)
        if not note_stem or not pdf_stem:
            continue
        if note_stem != pdf_stem:
            mismatches.append(
                f"{record.bibkey}: note='{record.note_path}' pdf='{record.pdf_path}'"
            )
    return mismatches


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-root", required=True)
    parser.add_argument(
        "--strict-basename",
        action="store_true",
        help="Return a non-zero status when note/pdf basenames do not match.",
    )
    args = parser.parse_args()

    workspace_root = Path(args.workspace_root).resolve()
    records = load_records(workspace_root)
    write_sqlite(workspace_root / "07-Resources" / "Papers" / "papers.sqlite", records)
    write_bib(workspace_root / "07-Resources" / "Papers" / "papers.bib", records)
    print(f"Synced {len(records)} paper records")
    mismatches = collect_basename_mismatches(records)
    if mismatches:
        print("Basename mismatches detected:", file=sys.stderr)
        for mismatch in mismatches:
            print(f"- {mismatch}", file=sys.stderr)
        if args.strict_basename:
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
