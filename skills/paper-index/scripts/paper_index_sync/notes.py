from __future__ import annotations

import ast
import json
import re
from pathlib import Path

from .config import workspace_display_path
from .models import PaperRecord


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


def normalize_tags(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    tags: list[str] = []
    seen: set[str] = set()
    for item in value:
        tag = str(item).strip()
        if not tag or tag in seen:
            continue
        tags.append(tag)
        seen.add(tag)
    return tags


def load_paper_records(workspace_root: Path, notes_dir: Path | None) -> list[PaperRecord]:
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
        tags = normalize_tags(frontmatter.get("tags", []))
        tags_json = json.dumps(tags, ensure_ascii=False)
        zotero_key = str(frontmatter.get("zotero_key", bibkey)).strip() or bibkey
        zotero_select = str(
            frontmatter.get("zotero_select", f"zotero://select/items/@{zotero_key}")
        ).strip()
        year_value = frontmatter.get("year")
        records.append(
            PaperRecord(
                bibkey=bibkey,
                title=extract_title(note_path),
                author=str(frontmatter.get("author", "")).strip(),
                year=year_value if isinstance(year_value, int) else None,
                venue=str(frontmatter.get("venue", "")).strip(),
                doi=str(frontmatter.get("doi", "")).strip(),
                area=str(frontmatter.get("area", "")).strip(),
                status=str(frontmatter.get("status", "")).strip(),
                note_path=workspace_display_path(note_path, workspace_root),
                pdf_path=normalize_rel_path(frontmatter.get("source", "")),
                zotero_key=zotero_key,
                zotero_select=zotero_select,
                short_title_zh=str(frontmatter.get("short_title_zh", "")).strip(),
                tags=tags,
                tags_json=tags_json,
            )
        )
    return records
