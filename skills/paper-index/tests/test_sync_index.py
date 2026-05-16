from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from paper_index_sync.bibtex import (  # noqa: E402
    load_resource_records,
    plan_external_library_keywords_merge,
    plan_paper_bib_merge,
    write_paper_bib,
)
from paper_index_sync.models import PaperRecord, ResourceRecord  # noqa: E402
from paper_index_sync.sqlite_store import write_resource_sqlite  # noqa: E402


def paper_record(key: str, *, title: str = "Updated Title") -> PaperRecord:
    return PaperRecord(
        bibkey=key,
        title=title,
        author="Ada Lovelace and Alan Turing",
        year=2024,
        venue="SIGGRAPH",
        doi=f"10.0000/{key}",
        area="Graphics/Test",
        status="not_started",
        note_path=f"07-Resources/Papers/{key}.md",
        pdf_path=f"D:/KnowledgeLibrary/papers/{key}.pdf",
        zotero_key=key,
        zotero_select=f"zotero://select/items/@{key}",
        short_title_zh="测试",
        tags=["paper", "graphics", "rendering"],
        tags_json="[]",
    )


def resource_record(key: str, *, title: str = "Resource") -> ResourceRecord:
    return ResourceRecord(
        key=key,
        kind="paper",
        title=title,
        author="Ada Lovelace",
        year=2024,
        doi=f"10.0000/{key}",
        keywords="Graphics/Test",
        note_path="",
        zotero_select=f"zotero://select/items/@{key}",
        bib_path="07-Resources/Papers/papers.bib",
    )


def test_paper_bib_merge_preserves_bib_only_updates_note_and_adds_note(tmp_path: Path) -> None:
    bib_path = tmp_path / "papers.bib"
    bib_path.write_text(
        """@misc{bib_only,
  title = {Keep Me},
  note = {preserve original body}
}

@misc{note_key,
  title = {Old Title}
}
""",
        encoding="utf-8",
    )

    records = [
        paper_record("note_key", title="New Title"),
        paper_record("new_note", title="Brand New"),
    ]
    plan = plan_paper_bib_merge(bib_path, records)

    assert plan.summary.preserved == 1
    assert plan.summary.updated == 1
    assert plan.summary.added == 1
    assert "note = {preserve original body}" in plan.text
    assert "@inproceedings{note_key," in plan.text
    assert "title = {New Title}" in plan.text
    assert "keywords = {Graphics/Test; graphics; rendering}" in plan.text
    assert "Graphics/Test; paper;" not in plan.text
    assert "@inproceedings{new_note," in plan.text

    write_paper_bib(bib_path, records)
    written = bib_path.read_text(encoding="utf-8")
    assert "note = {preserve original body}" in written
    assert "title = {Brand New}" in written


def test_resource_sqlite_preserves_deep_read_status_and_requires_prune(tmp_path: Path) -> None:
    db_path = tmp_path / "resources.sqlite"
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE resources (
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
        conn.execute(
            """
            INSERT INTO resources (
                key, kind, title, updated_at, deep_read_status
            ) VALUES
                ('keep', 'paper', 'Old', 'old-time', 'done'),
                ('stale', 'paper', 'Stale', 'old-time', 'queued')
            """
        )
        conn.commit()
    finally:
        conn.close()

    write_resource_sqlite(
        db_path,
        [resource_record("keep", title="Updated"), resource_record("new", title="New")],
        prune_stale=False,
    )
    conn = sqlite3.connect(db_path)
    try:
        rows = dict(conn.execute("SELECT key, deep_read_status FROM resources"))
        keep_title = conn.execute("SELECT title FROM resources WHERE key = 'keep'").fetchone()[0]
        assert rows["keep"] == "done"
        assert rows["new"] == "not_started"
        assert rows["stale"] == "queued"
        assert keep_title == "Updated"
    finally:
        conn.close()

    write_resource_sqlite(db_path, [resource_record("keep")], prune_stale=True)
    conn = sqlite3.connect(db_path)
    try:
        keys = {row[0] for row in conn.execute("SELECT key FROM resources")}
        assert keys == {"keep"}
    finally:
        conn.close()


def test_external_library_keywords_merge_preserves_pdf_and_other_fields(tmp_path: Path) -> None:
    external_bib = tmp_path / "library.bib"
    external_bib.write_text(
        """@misc{note_key,
  author = {Original Author},
  title = {Original Title},
  keywords = {Old/Keyword},
  pdf = {D:/KnowledgeLibrary/papers/note_key.pdf}
}

@misc{bib_only,
  title = {Bib Only},
  pdf = {D:/KnowledgeLibrary/papers/bib_only.pdf}
}

@misc{untouched,
  title = {Untouched},
  pdf = {D:/KnowledgeLibrary/papers/untouched.pdf}
}
""",
        encoding="utf-8",
    )
    records = [
        resource_record("note_key", title="Ignored",),
        resource_record("bib_only", title="Ignored"),
    ]
    records[0].keywords = "Graphics/Test; graphics; rendering"
    records[1].keywords = "Books/Reference"

    plan = plan_external_library_keywords_merge(external_bib, records)

    assert plan.matched == 2
    assert plan.changed == 2
    assert plan.missing == 0
    assert "author = {Original Author}" in plan.text
    assert "title = {Original Title}" in plan.text
    assert "pdf = {D:/KnowledgeLibrary/papers/note_key.pdf}" in plan.text
    assert "keywords = {Graphics/Test; graphics; rendering}" in plan.text
    assert "keywords = {Books/Reference}" in plan.text
    assert "@misc{untouched" in plan.text


def test_resource_records_use_note_tags_before_bib_keywords(tmp_path: Path) -> None:
    workspace = tmp_path
    paper_bib = workspace / "papers.bib"
    paper_bib.write_text(
        """@misc{note_key,
  title = {Old},
  keywords = {Old/Keyword}
}

@misc{bib_only,
  title = {Bib Only},
  keywords = {Bib/Only; imported}
}
""",
        encoding="utf-8",
    )

    records = load_resource_records(
        workspace,
        [paper_record("note_key")],
        {"paper": paper_bib},
    )
    by_key = {record.key: record for record in records}

    assert by_key["note_key"].keywords == "Graphics/Test; graphics; rendering"
    assert by_key["bib_only"].keywords == "Bib/Only; imported"


def test_cli_dry_run_does_not_modify_bib_or_sqlite(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    paper_dir = workspace / "07-Resources" / "Papers"
    book_dir = workspace / "07-Resources" / "Books"
    ref_dir = workspace / "07-Resources" / "Reference-Notes"
    paper_dir.mkdir(parents=True)
    book_dir.mkdir(parents=True)
    ref_dir.mkdir(parents=True)

    (paper_dir / "papers.bib").write_text(
        "@misc{bib_only,\n  title = {Keep Me}\n}\n",
        encoding="utf-8",
    )
    external_bib = workspace / "library.bib"
    external_bib.write_text(
        "@misc{bib_only,\n  title = {Keep Me},\n  pdf = {D:/KnowledgeLibrary/papers/bib_only.pdf}\n}\n",
        encoding="utf-8",
    )
    (book_dir / "books.bib").write_text("", encoding="utf-8")
    (ref_dir / "reference-notes.bib").write_text("", encoding="utf-8")
    (paper_dir / "note_key.md").write_text(
        """---
type: paper
bibkey: note_key
author: Ada Lovelace
year: 2024
venue: SIGGRAPH
area: Graphics/Test
tags: [paper, graphics, rendering]
---
# Note Title
""",
        encoding="utf-8",
    )
    config_path = workspace / ".paper-skills.json"
    config_path.write_text(
        json.dumps(
            {
                "paper_notes_dir": "07-Resources/Papers",
                "resource_bibs": {
                    "paper": "07-Resources/Papers/papers.bib",
                    "book": "07-Resources/Books/books.bib",
                    "reference-note": "07-Resources/Reference-Notes/reference-notes.bib",
                },
                "paper_sqlite": "07-Resources/Papers/papers.sqlite",
                "resource_sqlite": "07-Resources/resources.sqlite",
                "external_library_bib": "library.bib",
            }
        ),
        encoding="utf-8",
    )
    db_path = workspace / "07-Resources" / "resources.sqlite"
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE resources (
                key TEXT PRIMARY KEY,
                kind TEXT NOT NULL,
                title TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                deep_read_status TEXT NOT NULL DEFAULT 'not_started'
            )
            """
        )
        conn.execute(
            "INSERT INTO resources (key, kind, title, updated_at, deep_read_status) VALUES ('stale', 'paper', 'Stale', 'old', 'done')"
        )
        conn.commit()
    finally:
        conn.close()

    before_bib = (paper_dir / "papers.bib").read_text(encoding="utf-8")
    before_external = external_bib.read_text(encoding="utf-8")
    before_count = sqlite3.connect(db_path).execute("SELECT count(*) FROM resources").fetchone()[0]

    script = SCRIPTS_DIR / "sync_index.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--workspace-root",
            str(workspace),
            "--config",
            str(config_path),
            "--dry-run",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    assert "dry run: True" in result.stdout
    assert "Paper bib merge: preserved=1, updated=0, added=1" in result.stdout
    assert "External library keywords:" in result.stdout
    assert (paper_dir / "papers.bib").read_text(encoding="utf-8") == before_bib
    assert external_bib.read_text(encoding="utf-8") == before_external
    after_count = sqlite3.connect(db_path).execute("SELECT count(*) FROM resources").fetchone()[0]
    assert after_count == before_count
