from __future__ import annotations

import argparse
import ast
import json
import re
import sqlite3
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


RESOURCE_KINDS = ("paper", "book", "reference-note")
DISCOVERABLE_BIBS = {
    "paper": "papers.bib",
    "book": "books.bib",
    "reference-note": "reference-notes.bib",
}
SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "dist",
    "build",
}


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
    zotero_key: str
    zotero_select: str
    short_title_zh: str
    tags_json: str


@dataclass
class ResourceRecord:
    key: str
    kind: str
    title: str
    author: str
    year: int | None
    doi: str
    keywords: str
    note_path: str
    zotero_select: str
    bib_path: str


@dataclass
class IndexConfig:
    paper_notes_dir: Path | None = None
    resource_bibs: dict[str, Path] = field(default_factory=dict)
    paper_sqlite: Path | None = None
    resource_sqlite: Path | None = None


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


def workspace_display_path(path: Path, workspace_root: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(workspace_root)).replace("\\", "/")
    except ValueError:
        return str(resolved).replace("\\", "/")


def resolve_config_path(workspace_root: Path, value: object) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = workspace_root / path
    return path.resolve()


def iter_named_files(workspace_root: Path, filename: str) -> list[Path]:
    matches: list[Path] = []
    for path in workspace_root.rglob(filename):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file():
            matches.append(path.resolve())
    return sorted(matches)


def unique_discovered_file(workspace_root: Path, filename: str) -> Path | None:
    matches = iter_named_files(workspace_root, filename)
    if len(matches) > 1:
        rendered = "\n".join(f"- {workspace_display_path(path, workspace_root)}" for path in matches)
        raise SystemExit(
            f"Multiple {filename} candidates found. Pass --config or an explicit path.\n{rendered}"
        )
    return matches[0] if matches else None


def common_parent(paths: list[Path]) -> Path | None:
    if not paths:
        return None
    common = Path(paths[0]).resolve()
    if common.is_file():
        common = common.parent
    for path in paths[1:]:
        candidate = Path(path).resolve()
        if candidate.is_file():
            candidate = candidate.parent
        while common != common.parent and common not in (candidate, *candidate.parents):
            common = common.parent
    return common


def config_from_json(workspace_root: Path, config_path: Path) -> IndexConfig:
    data = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"Config must be a JSON object: {config_path}")

    resource_bibs: dict[str, Path] = {}
    raw_bibs = data.get("resource_bibs", {})
    if isinstance(raw_bibs, dict):
        for kind in RESOURCE_KINDS:
            path = resolve_config_path(workspace_root, raw_bibs.get(kind))
            if path is not None:
                resource_bibs[kind] = path

    return IndexConfig(
        paper_notes_dir=resolve_config_path(workspace_root, data.get("paper_notes_dir")),
        resource_bibs=resource_bibs,
        paper_sqlite=resolve_config_path(workspace_root, data.get("paper_sqlite")),
        resource_sqlite=resolve_config_path(workspace_root, data.get("resource_sqlite")),
    )


def discover_config(workspace_root: Path) -> IndexConfig:
    resource_bibs: dict[str, Path] = {}
    for kind, filename in DISCOVERABLE_BIBS.items():
        path = unique_discovered_file(workspace_root, filename)
        if path is not None:
            resource_bibs[kind] = path

    paper_bib = resource_bibs.get("paper")
    paper_notes_dir = paper_bib.parent if paper_bib is not None else None

    discovered_paper_sqlite = unique_discovered_file(workspace_root, "papers.sqlite")
    if discovered_paper_sqlite is None and paper_bib is not None:
        discovered_paper_sqlite = paper_bib.parent / "papers.sqlite"

    discovered_resource_sqlite = unique_discovered_file(workspace_root, "resources.sqlite")
    if discovered_resource_sqlite is None:
        parent = common_parent(list(resource_bibs.values()))
        if parent is not None:
            discovered_resource_sqlite = parent / "resources.sqlite"

    return IndexConfig(
        paper_notes_dir=paper_notes_dir,
        resource_bibs=resource_bibs,
        paper_sqlite=discovered_paper_sqlite,
        resource_sqlite=discovered_resource_sqlite,
    )


def load_index_config(workspace_root: Path, config_path: Path | None) -> IndexConfig:
    if config_path is not None:
        return config_from_json(workspace_root, config_path.resolve())
    default_config = workspace_root / ".paper-skills.json"
    if default_config.exists():
        return config_from_json(workspace_root, default_config)
    return discover_config(workspace_root)


def apply_cli_overrides(config: IndexConfig, workspace_root: Path, args: argparse.Namespace) -> IndexConfig:
    if args.paper_notes_dir:
        config.paper_notes_dir = resolve_config_path(workspace_root, args.paper_notes_dir)
    for kind, attr in (
        ("paper", "paper_bib"),
        ("book", "book_bib"),
        ("reference-note", "reference_note_bib"),
    ):
        path = resolve_config_path(workspace_root, getattr(args, attr))
        if path is not None:
            config.resource_bibs[kind] = path
    if args.paper_sqlite:
        config.paper_sqlite = resolve_config_path(workspace_root, args.paper_sqlite)
    if args.resource_sqlite:
        config.resource_sqlite = resolve_config_path(workspace_root, args.resource_sqlite)
    return config


def load_records(workspace_root: Path, notes_dir: Path | None) -> list[PaperRecord]:
    if notes_dir is None or not notes_dir.exists():
        return []
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
        zotero_key = str(frontmatter.get("zotero_key", bibkey)).strip() or bibkey
        zotero_select = str(
            frontmatter.get("zotero_select", f"zotero://select/items/@{zotero_key}")
        ).strip()
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
                note_path=workspace_display_path(note_path, workspace_root),
                pdf_path=normalize_rel_path(frontmatter.get("source", "")),
                zotero_key=zotero_key,
                zotero_select=zotero_select,
                short_title_zh=str(frontmatter.get("short_title_zh", "")).strip(),
                tags_json=tags_json,
            )
        )
    return records


def parse_bib_entries(bib_path: Path, kind: str, workspace_root: Path) -> list[ResourceRecord]:
    if not bib_path.exists():
        return []
    text = bib_path.read_text(encoding="utf-8")
    matches = list(re.finditer(r"@(?P<type>[A-Za-z]+)\s*\{\s*(?P<key>[^,\s]+)\s*,", text))
    records: list[ResourceRecord] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[start:end]

        def field(name: str) -> str:
            field_match = re.search(
                rf"^\s*{re.escape(name)}\s*=\s*\{{(?P<value>.*?)\}}\s*,?\s*$",
                body,
                flags=re.IGNORECASE | re.MULTILINE,
            )
            return field_match.group("value").strip() if field_match else ""

        key = match.group("key").strip()
        year_text = field("year")
        records.append(
            ResourceRecord(
                key=key,
                kind=kind,
                title=field("title") or key,
                author=field("author"),
                year=int(year_text) if re.fullmatch(r"\d{4}", year_text) else None,
                doi=field("doi"),
                keywords=field("keywords"),
                note_path="",
                zotero_select=f"zotero://select/items/@{key}",
                bib_path=workspace_display_path(bib_path, workspace_root),
            )
        )
    return records


def load_resource_records(
    workspace_root: Path,
    paper_records: list[PaperRecord],
    resource_bibs: dict[str, Path],
) -> list[ResourceRecord]:
    paper_note_by_key = {record.bibkey: record.note_path for record in paper_records}
    records: list[ResourceRecord] = []
    for kind in RESOURCE_KINDS:
        bib_path = resource_bibs.get(kind)
        if bib_path is None:
            continue
        for record in parse_bib_entries(bib_path, kind, workspace_root):
            if kind == "paper":
                record.note_path = paper_note_by_key.get(record.key, "")
            records.append(record)
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
                pdf_path TEXT,
                zotero_key TEXT,
                zotero_select TEXT,
                short_title_zh TEXT,
                tags_json TEXT NOT NULL DEFAULT '[]',
                updated_at TEXT NOT NULL
            )
            """
        )
        table_info = list(conn.execute("PRAGMA table_info(papers)"))
        columns = {row[1] for row in table_info}
        pdf_path_not_null = any(row[1] == "pdf_path" and row[3] for row in table_info)
        if pdf_path_not_null:
            conn.execute("ALTER TABLE papers RENAME TO papers_legacy")
            conn.execute(
                """
                CREATE TABLE papers (
                    bibkey TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    author TEXT,
                    year INTEGER,
                    venue TEXT,
                    doi TEXT,
                    area TEXT,
                    status TEXT,
                    note_path TEXT NOT NULL,
                    pdf_path TEXT,
                    zotero_key TEXT,
                    zotero_select TEXT,
                    short_title_zh TEXT,
                    tags_json TEXT NOT NULL DEFAULT '[]',
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                INSERT INTO papers (
                    bibkey, title, author, year, venue, doi, area, status, note_path,
                    pdf_path, short_title_zh, tags_json, updated_at
                )
                SELECT
                    bibkey, title, author, year, venue, doi, area, status, note_path,
                    pdf_path, short_title_zh, tags_json, updated_at
                FROM papers_legacy
                """
            )
            conn.execute("DROP TABLE papers_legacy")
            table_info = list(conn.execute("PRAGMA table_info(papers)"))
            columns = {row[1] for row in table_info}
        if "zotero_key" not in columns:
            conn.execute("ALTER TABLE papers ADD COLUMN zotero_key TEXT")
        if "zotero_select" not in columns:
            conn.execute("ALTER TABLE papers ADD COLUMN zotero_select TEXT")
        existing_keys = {row[0] for row in conn.execute("SELECT bibkey FROM papers")}
        incoming_keys = {record.bibkey for record in records}
        stale_keys = existing_keys - incoming_keys
        if stale_keys:
            conn.executemany("DELETE FROM papers WHERE bibkey = ?", [(key,) for key in stale_keys])
        now = datetime.now(timezone.utc).isoformat()
        conn.executemany(
            """
            INSERT INTO papers (
                bibkey, title, author, year, venue, doi, area, status, note_path, pdf_path,
                zotero_key, zotero_select, short_title_zh, tags_json, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                zotero_key=excluded.zotero_key,
                zotero_select=excluded.zotero_select,
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
                    record.pdf_path or None,
                    record.zotero_key,
                    record.zotero_select,
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


def write_resource_sqlite(db_path: Path, records: list[ResourceRecord]) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS resources (
                key TEXT PRIMARY KEY,
                kind TEXT NOT NULL,
                title TEXT NOT NULL,
                author TEXT,
                year INTEGER,
                doi TEXT,
                keywords TEXT,
                note_path TEXT,
                zotero_select TEXT,
                bib_path TEXT,
                updated_at TEXT NOT NULL
            )
            """
        )
        existing_keys = {row[0] for row in conn.execute("SELECT key FROM resources")}
        incoming_keys = {record.key for record in records}
        stale_keys = existing_keys - incoming_keys
        if stale_keys:
            conn.executemany("DELETE FROM resources WHERE key = ?", [(key,) for key in stale_keys])
        now = datetime.now(timezone.utc).isoformat()
        conn.executemany(
            """
            INSERT INTO resources (
                key, kind, title, author, year, doi, keywords, note_path,
                zotero_select, bib_path, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                kind=excluded.kind,
                title=excluded.title,
                author=excluded.author,
                year=excluded.year,
                doi=excluded.doi,
                keywords=excluded.keywords,
                note_path=excluded.note_path,
                zotero_select=excluded.zotero_select,
                bib_path=excluded.bib_path,
                updated_at=excluded.updated_at
            """,
            [
                (
                    record.key,
                    record.kind,
                    record.title,
                    record.author,
                    record.year,
                    record.doi,
                    record.keywords,
                    record.note_path,
                    record.zotero_select,
                    record.bib_path,
                    now,
                )
                for record in records
            ],
        )
        conn.commit()
    finally:
        conn.close()


def bib_type_for(record: PaperRecord) -> str:
    venue = record.venue.lower()
    if "neurips" in venue or "siggraph" in venue or "iclr" in venue:
        return "inproceedings"
    if "journal" in venue or "forum" in venue:
        return "article"
    return "misc"


def bib_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")


def format_person_name(name: str) -> str:
    name = name.strip()
    if not name or "," in name:
        return name
    parts = name.split()
    if len(parts) < 2:
        return name
    return f"{parts[-1]}, {' '.join(parts[:-1])}"


def format_author_field(author: str) -> str:
    author = author.strip()
    if not author:
        return ""
    if " and " in author:
        return " and ".join(format_person_name(part) for part in author.split(" and "))
    comma_parts = [part.strip() for part in author.split(",") if part.strip()]
    if len(comma_parts) > 1:
        return " and ".join(format_person_name(part) for part in comma_parts)
    return format_person_name(author)


def write_bib(bib_path: Path, records: list[PaperRecord]) -> None:
    bib_path.parent.mkdir(parents=True, exist_ok=True)
    chunks: list[str] = []
    for record in records:
        fields: list[tuple[str, str]] = [
            ("author", format_author_field(record.author)),
            ("title", record.title),
        ]
        if record.year is not None:
            fields.append(("year", str(record.year)))
        bib_type = bib_type_for(record)
        if record.venue:
            key = "journal" if bib_type == "article" else "booktitle" if bib_type == "inproceedings" else "note"
            fields.append((key, record.venue))
        elif record.area:
            fields.append(("keywords", record.area))
        if record.area and record.venue:
            fields.append(("keywords", record.area))
        if record.doi:
            fields.append(("doi", record.doi))
        rendered = ",\n".join(f"  {key} = {{{bib_escape(value)}}}" for key, value in fields if value)
        chunks.append(f"@{bib_type}{{{record.bibkey},\n{rendered}\n}}")
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


def print_config_summary(config: IndexConfig, workspace_root: Path) -> None:
    def show(path: Path | None) -> str:
        return workspace_display_path(path, workspace_root) if path is not None else "<none>"

    print("Index targets:")
    print(f"- paper notes: {show(config.paper_notes_dir)}")
    for kind in RESOURCE_KINDS:
        print(f"- {kind} bib: {show(config.resource_bibs.get(kind))}")
    print(f"- paper sqlite: {show(config.paper_sqlite)}")
    print(f"- resource sqlite: {show(config.resource_sqlite)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-root", required=True)
    parser.add_argument("--config", type=Path, help="Path to a downstream .paper-skills.json config.")
    parser.add_argument("--paper-notes-dir")
    parser.add_argument("--paper-bib")
    parser.add_argument("--book-bib")
    parser.add_argument("--reference-note-bib")
    parser.add_argument("--paper-sqlite")
    parser.add_argument("--resource-sqlite")
    parser.add_argument(
        "--strict-basename",
        action="store_true",
        help="Return a non-zero status when note/pdf basenames do not match.",
    )
    args = parser.parse_args()

    workspace_root = Path(args.workspace_root).resolve()
    config = load_index_config(workspace_root, args.config)
    config = apply_cli_overrides(config, workspace_root, args)

    has_paper_notes = config.paper_notes_dir is not None and config.paper_notes_dir.exists()
    records = load_records(workspace_root, config.paper_notes_dir)

    if has_paper_notes and config.paper_sqlite is not None:
        write_sqlite(config.paper_sqlite, records)
    if has_paper_notes and "paper" in config.resource_bibs:
        write_bib(config.resource_bibs["paper"], records)

    resource_records = load_resource_records(workspace_root, records, config.resource_bibs)
    if config.resource_sqlite is not None:
        write_resource_sqlite(config.resource_sqlite, resource_records)

    print_config_summary(config, workspace_root)
    print(f"Synced {len(records)} paper records")
    print(f"Synced {len(resource_records)} resource records")
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
