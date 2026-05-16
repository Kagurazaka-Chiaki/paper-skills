---
name: paper-index
description: Maintain lightweight repository resource indexes using minimal BibTeX files and SQLite catalogs, syncing stable keys, note paths, Zotero links, and minimal metadata for already-identified papers, books, and reference notes. Use when Codex needs to initialize, refresh, repair, or append repository-local minimal `.bib`, `papers.sqlite`, or `resources.sqlite` indexes after bibkey, rename, organize, or note updates.
---

# Paper Index

## Purpose

Maintain lightweight repository-level resource databases using minimal BibTeX files and SQLite catalogs.

Use this skill after resource identity is already known and a stable key exists or is being finalized.

## Reads

- existing resource notes or metadata records
- optional existing `papers.bib`
- optional existing `papers.sqlite`
- optional existing `resources.sqlite`
- stable identifiers such as `bibkey`, title, year, DOI, and note path

## Writes

- created or updated `papers.bib`
- created or updated `papers.sqlite`
- created or updated `resources.sqlite`
- optional `bibkey:` sync into existing notes when the workflow explicitly includes it

## Source Of Truth

- stable `bibkey`
- current note paths and Zotero links
- note frontmatter metadata when present
- existing index files when already established
- the Python sync script under `scripts/`

## Required Behavior

- call the Python sync script instead of manually rebuilding the database in prose
- keep repository `.bib` files human-readable and keep SQLite catalogs lightweight
- treat repository `.bib`, `papers.sqlite`, and `resources.sqlite` as repository indexes, not as full bibliographic warehouses
- use the stable `bibkey` as the primary key in `papers.sqlite`
- use the stable resource key as the primary key in `resources.sqlite`
- preserve the existing readable `short_title_zh` spacing convention, including spaces at Chinese-English boundaries when present
- preserve existing entries unless the current paper record clearly supersedes them
- update paths and core metadata conservatively instead of rewriting unrelated entries
- stop and report collisions when two different papers appear to claim the same `bibkey`
- prefer recoverable metadata over guessed metadata
- keep repository `papers.bib` free of `pdf`, `file`, and `x_note` attachment fields
- treat configured external bibliography files as Zotero import sources when attachment paths are needed

## Non-Goals

- matching unknown PDFs
- inventing bibkeys when identity is still unresolved
- renaming PDFs or notes
- deciding final archive layout
- writing or rewriting note bodies
- converting the index into a heavyweight schema or external database

## Output Contract

Report at least:

- target bibkey or batch scope
- whether `papers.bib` changed
- whether `papers.sqlite` changed
- whether `resources.sqlite` changed
- which paths or metadata fields were added or updated
- any collisions or ambiguous records that blocked the update

## Workflow

1. Inspect the current local paper state.
   Confirm the paper identity, stable `bibkey`, note path, and Zotero key/link.

2. Inspect the current indexes.
   Read repository `.bib` files, `papers.sqlite`, and `resources.sqlite` when they exist.
   Preserve the existing shape instead of redesigning the index on each run.

3. Run the Python sync script.
   Use:
   - `python scripts/sync_index.py --workspace-root <workspace-root> --config <workspace-root>/.paper-skills.json`
   - or `python scripts/sync_index.py --workspace-root <workspace-root>` when discoverable filenames are unique
   - optionally narrow the run to one note or one `bibkey` when the task is intentionally scoped

4. Update `papers.bib`.
   Create or update one entry for the paper using the closest confident BibTeX type.
   Keep fields minimal and avoid speculative bibliography cleanup.
   Do not include `pdf`, `file`, or `x_note` fields in the current repository convention.

5. Update `papers.sqlite` and `resources.sqlite`.
   Create or upsert one row per paper keyed by the same `bibkey`.
   Create or upsert one row per resource in `resources.sqlite`.
   Keep schemas flat and explicit so they remain easy to inspect with standard SQLite tools.

6. Sync note metadata only when needed.
   If the note lacks `bibkey:` or another directly related stable field, write the missing value.
   Do not rewrite unrelated note content.

## Default Index Shape

Use project configuration when available. A downstream workspace may provide `.paper-skills.json` at its root:

```json
{
  "paper_notes_dir": "<relative-or-absolute-paper-note-dir>",
  "resource_bibs": {
    "paper": "<relative-or-absolute-papers.bib>",
    "book": "<relative-or-absolute-books.bib>",
    "reference-note": "<relative-or-absolute-reference-notes.bib>"
  },
  "paper_sqlite": "<relative-or-absolute-papers.sqlite>",
  "resource_sqlite": "<relative-or-absolute-resources.sqlite>",
  "external_library_bib": "<relative-or-absolute-zotero-import-bib>",
  "external_pdf_roots": {
    "paper": "<relative-or-absolute-paper-pdf-root>",
    "book": "<relative-or-absolute-book-pdf-root>",
    "reference-note": "<relative-or-absolute-reference-note-pdf-root>"
  }
}
```

When no config is supplied, the script only uses discoverable filenames:

- `papers.bib`
- `books.bib`
- `reference-notes.bib`
- `papers.sqlite`
- `resources.sqlite`

If multiple candidates exist, stop and ask the user to provide `--config` or explicit CLI paths.

For `papers.sqlite`, prefer one main table:

- `papers(bibkey TEXT PRIMARY KEY, title TEXT, author TEXT, year INTEGER, venue TEXT, doi TEXT, area TEXT, status TEXT, note_path TEXT, pdf_path TEXT, zotero_key TEXT, zotero_select TEXT, short_title_zh TEXT, tags_json TEXT, updated_at TEXT)`

For `resources.sqlite`, prefer one main table:

- `resources(key TEXT PRIMARY KEY, kind TEXT, title TEXT, author TEXT, year INTEGER, doi TEXT, keywords TEXT, note_path TEXT, zotero_select TEXT, bib_path TEXT, updated_at TEXT)`

## Script

Use the bundled script:

- `scripts/sync_index.py`

It should:

- scan the configured paper note directory when one exists
- read configured minimal `.bib` files, or uniquely discovered `papers.bib`, `books.bib`, and `reference-notes.bib`
- parse frontmatter conservatively
- ignore non-paper notes such as `README.md`
- upsert rows into the configured or discovered `papers.sqlite`
- upsert rows into the configured or discovered `resources.sqlite`
- rewrite `papers.bib` from the same stable record set

## Output Discipline

- Keep the index files easy for humans to inspect.
- Prefer one stable entry per paper over duplicated aliases.
- If the main task is generating the `bibkey`, use `$paper-bibkey` first.
- If the main task is renaming the PDF, use `$paper-rename` first.
- If the main task is placing the PDF in its final archive location, use `$paper-organize` first.
- If the main task is collection-level coverage or duplicate state rather than maintaining the database indexes themselves, use `$paper-reconcile`.
