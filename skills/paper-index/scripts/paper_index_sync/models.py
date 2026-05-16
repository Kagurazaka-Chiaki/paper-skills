from __future__ import annotations

from dataclasses import dataclass, field
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
    tags: list[str]
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
    external_library_bib: Path | None = None


@dataclass(frozen=True)
class SyncOptions:
    dry_run: bool = False
    prune_stale: bool = False
    strict_basename: bool = False


@dataclass(frozen=True)
class BibMergeSummary:
    preserved: int
    updated: int
    added: int


@dataclass(frozen=True)
class SqliteSyncSummary:
    incoming: int
    existing: int
    stale: int
