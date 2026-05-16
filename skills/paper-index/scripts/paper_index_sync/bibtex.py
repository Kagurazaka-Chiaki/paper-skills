from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .config import workspace_display_path
from .models import BibMergeSummary, PaperRecord, ResourceRecord


ENTRY_RE = re.compile(r"@(?P<type>[A-Za-z]+)\s*\{\s*(?P<key>[^,\s]+)\s*,")


@dataclass(frozen=True)
class BibEntry:
    entry_type: str
    key: str
    body: str


@dataclass(frozen=True)
class BibMergePlan:
    text: str
    summary: BibMergeSummary


@dataclass(frozen=True)
class ExternalKeywordMergePlan:
    text: str
    matched: int
    changed: int
    unchanged: int
    missing: int


def split_bib_entries(text: str) -> list[BibEntry]:
    matches = list(ENTRY_RE.finditer(text))
    entries: list[BibEntry] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        entries.append(
            BibEntry(
                entry_type=match.group("type"),
                key=match.group("key").strip(),
                body=text[start:end].strip(),
            )
        )
    return entries


def read_bib_entries(bib_path: Path) -> list[BibEntry]:
    if not bib_path.exists():
        return []
    return split_bib_entries(bib_path.read_text(encoding="utf-8-sig"))


def field_value(entry_body: str, name: str) -> str:
    match = re.search(
        rf"^\s*{re.escape(name)}\s*=\s*\{{(?P<value>.*?)\}}\s*,?\s*$",
        entry_body,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    return match.group("value").strip() if match else ""


def replace_or_insert_field(entry_body: str, field_name: str, field_text: str) -> str:
    pattern = re.compile(
        rf"(?ms)^(\s*){re.escape(field_name)}\s*=\s*\{{.*?\}}\s*,?\s*$",
        flags=re.IGNORECASE | re.MULTILINE,
    )
    replacement = f"  {field_name} = {{{bib_escape(field_text)}}},"
    if pattern.search(entry_body):
        return pattern.sub(replacement, entry_body, count=1)
    insert_at = entry_body.rfind("\n}")
    if insert_at == -1:
        return entry_body
    before = entry_body[:insert_at].rstrip()
    if before.endswith(","):
        return before + "\n" + replacement + entry_body[insert_at:]
    return before + ",\n" + replacement + entry_body[insert_at:]


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


def zotero_keyword_field(record: PaperRecord) -> str:
    values: list[str] = []
    seen: set[str] = set()
    for value in [record.area, *record.tags]:
        keyword = value.strip()
        if not keyword or keyword == "paper" or keyword in seen:
            continue
        values.append(keyword)
        seen.add(keyword)
    return "; ".join(values)


def render_paper_entry(record: PaperRecord) -> str:
    fields: list[tuple[str, str]] = [
        ("author", format_author_field(record.author)),
        ("title", record.title),
    ]
    if record.year is not None:
        fields.append(("year", str(record.year)))
    bib_type = bib_type_for(record)
    keywords = zotero_keyword_field(record)
    if record.venue:
        key = "journal" if bib_type == "article" else "booktitle" if bib_type == "inproceedings" else "note"
        fields.append((key, record.venue))
    if keywords:
        fields.append(("keywords", keywords))
    if record.doi:
        fields.append(("doi", record.doi))
    rendered = ",\n".join(f"  {key} = {{{bib_escape(value)}}}" for key, value in fields if value)
    return f"@{bib_type}{{{record.bibkey},\n{rendered}\n}}"


def plan_paper_bib_merge(bib_path: Path, paper_records: list[PaperRecord]) -> BibMergePlan:
    existing = read_bib_entries(bib_path)
    existing_keys = {entry.key for entry in existing}
    paper_by_key = {record.bibkey: record for record in paper_records}
    seen: set[str] = set()
    chunks: list[str] = []
    preserved = 0
    updated = 0

    for entry in existing:
        record = paper_by_key.get(entry.key)
        if record is None:
            chunks.append(entry.body)
            preserved += 1
        else:
            chunks.append(render_paper_entry(record))
            updated += 1
            seen.add(entry.key)

    added_records = [
        record
        for record in paper_records
        if record.bibkey not in seen and record.bibkey not in existing_keys
    ]
    for record in added_records:
        chunks.append(render_paper_entry(record))

    text = "\n\n".join(chunks) + ("\n" if chunks else "")
    return BibMergePlan(
        text=text,
        summary=BibMergeSummary(preserved=preserved, updated=updated, added=len(added_records)),
    )


def write_paper_bib(bib_path: Path, paper_records: list[PaperRecord]) -> BibMergeSummary:
    plan = plan_paper_bib_merge(bib_path, paper_records)
    bib_path.parent.mkdir(parents=True, exist_ok=True)
    bib_path.write_text(plan.text, encoding="utf-8", newline="\n")
    return plan.summary


def plan_external_library_keywords_merge(
    external_bib_path: Path,
    resource_records: list[ResourceRecord],
) -> ExternalKeywordMergePlan:
    if not external_bib_path.exists():
        return ExternalKeywordMergePlan(text="", matched=0, changed=0, unchanged=0, missing=len(resource_records))

    text = external_bib_path.read_text(encoding="utf-8-sig")
    matches = list(ENTRY_RE.finditer(text))
    keywords_by_key = {
        record.key: record.keywords.strip()
        for record in resource_records
        if record.key and record.keywords.strip()
    }
    seen: set[str] = set()
    chunks: list[str] = []
    changed = 0
    unchanged = 0

    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        key = match.group("key").strip()
        entry = text[start:end].strip()
        keywords = keywords_by_key.get(key)
        if keywords is None:
            chunks.append(entry)
        else:
            seen.add(key)
            existing = field_value(entry, "keywords")
            if existing == keywords:
                unchanged += 1
                chunks.append(entry)
            else:
                changed += 1
                chunks.append(replace_or_insert_field(entry, "keywords", keywords))

    missing = len(set(keywords_by_key) - seen)
    return ExternalKeywordMergePlan(
        text="\n\n".join(chunks) + ("\n" if chunks else ""),
        matched=len(seen),
        changed=changed,
        unchanged=unchanged,
        missing=missing,
    )


def write_external_library_keywords(
    external_bib_path: Path,
    resource_records: list[ResourceRecord],
) -> ExternalKeywordMergePlan:
    plan = plan_external_library_keywords_merge(external_bib_path, resource_records)
    if external_bib_path.exists():
        external_bib_path.write_text(plan.text, encoding="utf-8", newline="\n")
    return plan


def resource_from_bib_entry(entry: BibEntry, kind: str, bib_path: Path, workspace_root: Path) -> ResourceRecord:
    year_text = field_value(entry.body, "year")
    return ResourceRecord(
        key=entry.key,
        kind=kind,
        title=field_value(entry.body, "title") or entry.key,
        author=field_value(entry.body, "author"),
        year=int(year_text) if re.fullmatch(r"\d{4}", year_text) else None,
        doi=field_value(entry.body, "doi"),
        keywords=field_value(entry.body, "keywords"),
        note_path="",
        zotero_select=f"zotero://select/items/@{entry.key}",
        bib_path=workspace_display_path(bib_path, workspace_root),
    )


def resource_from_paper_record(record: PaperRecord, bib_path: Path, workspace_root: Path) -> ResourceRecord:
    return ResourceRecord(
        key=record.bibkey,
        kind="paper",
        title=record.title,
        author=record.author,
        year=record.year,
        doi=record.doi,
        keywords=zotero_keyword_field(record),
        note_path=record.note_path,
        zotero_select=record.zotero_select,
        bib_path=workspace_display_path(bib_path, workspace_root),
    )


def load_resource_records(
    workspace_root: Path,
    paper_records: list[PaperRecord],
    resource_bibs: dict[str, Path],
) -> list[ResourceRecord]:
    paper_by_key = {record.bibkey: record for record in paper_records}
    records: list[ResourceRecord] = []

    for kind, bib_path in ((kind, resource_bibs.get(kind)) for kind in ("paper", "book", "reference-note")):
        if bib_path is None:
            continue
        seen: set[str] = set()
        for entry in read_bib_entries(bib_path):
            seen.add(entry.key)
            if kind == "paper" and entry.key in paper_by_key:
                records.append(resource_from_paper_record(paper_by_key[entry.key], bib_path, workspace_root))
            else:
                records.append(resource_from_bib_entry(entry, kind, bib_path, workspace_root))
        if kind == "paper":
            for record in paper_records:
                if record.bibkey not in seen:
                    records.append(resource_from_paper_record(record, bib_path, workspace_root))
    return records
