from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .models import PaperRecord, ResourceRecord, SqliteSyncSummary


@dataclass(frozen=True)
class SqlitePlan:
    summary: SqliteSyncSummary
    stale_keys: set[str]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {str(row[1]) for row in conn.execute(f"PRAGMA table_info({table})")}


def existing_keys(db_path: Path, table: str, key_column: str) -> set[str]:
    if not db_path.exists():
        return set()
    conn = sqlite3.connect(db_path)
    try:
        tables = {str(row[0]) for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
        if table not in tables:
            return set()
        return {str(row[0]) for row in conn.execute(f"SELECT {key_column} FROM {table}")}
    finally:
        conn.close()


def plan_sqlite_sync(
    db_path: Path,
    table: str,
    key_column: str,
    incoming_keys: set[str],
) -> SqlitePlan:
    existing = existing_keys(db_path, table, key_column)
    stale = existing - incoming_keys
    return SqlitePlan(
        summary=SqliteSyncSummary(incoming=len(incoming_keys), existing=len(existing), stale=len(stale)),
        stale_keys=stale,
    )


def ensure_papers_schema(conn: sqlite3.Connection) -> None:
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
    info = list(conn.execute("PRAGMA table_info(papers)"))
    columns = {str(row[1]) for row in info}
    pdf_path_not_null = any(str(row[1]) == "pdf_path" and bool(row[3]) for row in info)
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
        columns = table_columns(conn, "papers")
    if "zotero_key" not in columns:
        conn.execute("ALTER TABLE papers ADD COLUMN zotero_key TEXT")
    if "zotero_select" not in columns:
        conn.execute("ALTER TABLE papers ADD COLUMN zotero_select TEXT")


def ensure_resources_schema(conn: sqlite3.Connection) -> None:
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
            updated_at TEXT NOT NULL,
            deep_read_status TEXT NOT NULL DEFAULT 'not_started'
        )
        """
    )
    columns = table_columns(conn, "resources")
    if "deep_read_status" not in columns:
        conn.execute(
            "ALTER TABLE resources ADD COLUMN deep_read_status TEXT NOT NULL DEFAULT 'not_started'"
        )


def write_paper_sqlite(db_path: Path, records: list[PaperRecord], *, prune_stale: bool) -> SqliteSyncSummary:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    incoming_keys = {record.bibkey for record in records}
    plan = plan_sqlite_sync(db_path, "papers", "bibkey", incoming_keys)
    conn = sqlite3.connect(db_path)
    try:
        ensure_papers_schema(conn)
        if prune_stale and plan.stale_keys:
            conn.executemany("DELETE FROM papers WHERE bibkey = ?", [(key,) for key in plan.stale_keys])
        now = utc_now()
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
        return plan.summary
    finally:
        conn.close()


def write_resource_sqlite(
    db_path: Path,
    records: list[ResourceRecord],
    *,
    prune_stale: bool,
) -> SqliteSyncSummary:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    incoming_keys = {record.key for record in records}
    plan = plan_sqlite_sync(db_path, "resources", "key", incoming_keys)
    conn = sqlite3.connect(db_path)
    try:
        ensure_resources_schema(conn)
        if prune_stale and plan.stale_keys:
            conn.executemany("DELETE FROM resources WHERE key = ?", [(key,) for key in plan.stale_keys])
        now = utc_now()
        conn.executemany(
            """
            INSERT INTO resources (
                key, kind, title, author, year, doi, keywords, note_path,
                zotero_select, bib_path, updated_at, deep_read_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'not_started')
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
        return plan.summary
    finally:
        conn.close()
