---
name: paper-index
description: Maintain a simple repository-level paper database using a BibTeX file and a SQLite catalog, syncing stable bibkeys, note paths, PDF paths, and minimal metadata for already-identified papers. Use when Codex needs to initialize, refresh, repair, or append a lightweight paper index after bibkey, rename, organize, or note updates.
---

# Paper Index

## Purpose

Maintain a lightweight repository-level paper database using a BibTeX file and a SQLite catalog.

Use this skill after paper identity is already known and a stable `bibkey` exists or is being finalized.

## Reads

- existing paper notes or metadata records
- existing attachment paths
- optional existing `papers.bib`
- optional existing `papers.sqlite`
- stable identifiers such as `bibkey`, title, year, DOI, and note path

## Writes

- created or updated `papers.bib`
- created or updated `papers.sqlite`
- optional `bibkey:` sync into existing notes when the workflow explicitly includes it

## Source Of Truth

- stable `bibkey`
- current note and PDF paths
- note frontmatter metadata when present
- existing index files when already established
- the Python sync script under `scripts/`

## Required Behavior

- call the Python sync script instead of manually rebuilding the database in prose
- keep `papers.bib` human-readable and keep `papers.sqlite` lightweight
- treat `papers.bib` and `papers.sqlite` as repository indexes, not as full bibliographic warehouses
- use the stable `bibkey` as the primary key in `papers.sqlite`
- preserve the existing readable `short_title_zh` spacing convention, including spaces at Chinese-English boundaries when present
- preserve existing entries unless the current paper record clearly supersedes them
- update paths and core metadata conservatively instead of rewriting unrelated entries
- stop and report collisions when two different papers appear to claim the same `bibkey`
- prefer recoverable metadata over guessed metadata
- keep `papers.bib` temporarily free of `file` and `x_note` fields

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
- which paths or metadata fields were added or updated
- any collisions or ambiguous records that blocked the update

## Workflow

1. Inspect the current local paper state.
   Confirm the paper identity, stable `bibkey`, note path, and PDF path.

2. Inspect the current indexes.
   Read `papers.bib` and `papers.sqlite` when they exist.
   Preserve the existing shape instead of redesigning the index on each run.

3. Run the Python sync script.
   Use:
   - `python scripts/sync_index.py --workspace-root <workspace-root>`
   - optionally narrow the run to one note or one `bibkey` when the task is intentionally scoped

4. Update `papers.bib`.
   Create or update one entry for the paper using the closest confident BibTeX type.
   Keep fields minimal and avoid speculative bibliography cleanup.
   Do not include `file` or `x_note` fields in the current repository convention.

5. Update `papers.sqlite`.
   Create or upsert one row per paper keyed by the same `bibkey`.
   Keep the schema flat and explicit so it remains easy to inspect with standard SQLite tools.

6. Sync note metadata only when needed.
   If the note lacks `bibkey:` or another directly related stable field, write the missing value.
   Do not rewrite unrelated note content.

## Default Index Shape

Use simple repository-level paths when the workspace does not already define others:

- `07-Resources/Papers/papers.bib`
- `07-Resources/Papers/papers.sqlite`

For `papers.sqlite`, prefer one main table:

- `papers(bibkey TEXT PRIMARY KEY, title TEXT, author TEXT, year INTEGER, venue TEXT, doi TEXT, area TEXT, status TEXT, note_path TEXT, pdf_path TEXT, short_title_zh TEXT, tags_json TEXT, updated_at TEXT)`

## Script

Use the bundled script:

- `scripts/sync_index.py`

It should:

- scan `07-Resources/Papers/*.md`
- parse frontmatter conservatively
- ignore non-paper notes such as `README.md`
- upsert rows into `papers.sqlite`
- rewrite `papers.bib` from the same stable record set

## Output Discipline

- Keep the index files easy for humans to inspect.
- Prefer one stable entry per paper over duplicated aliases.
- If the main task is generating the `bibkey`, use `$paper-bibkey` first.
- If the main task is renaming the PDF, use `$paper-rename` first.
- If the main task is placing the PDF in its final archive location, use `$paper-organize` first.
- If the main task is collection-level coverage or duplicate state rather than maintaining the database indexes themselves, use `$paper-reconcile`.
