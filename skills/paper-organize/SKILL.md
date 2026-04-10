---
name: paper-organize
description: Organize already-keyed paper PDFs into their final library location, using provided metadata and the local workspace's structure rules to choose the destination path, preview or execute the move, update the local paper index or catalog when one exists, update direct note attachment references, and report whether duplicates were detected. Use when Codex needs to decide where a paper should live in the current library, align an incoming paper with the existing archive structure, or perform the final archive move after bibkey and filename are already settled.
---

# Paper Organize

## Purpose

Place a paper PDF into its final archive location after identity and filename are already stable.

## Reads

- PDF path
- confirmed `bibkey`
- optional metadata such as `title`, `year`, `doi`, and `area`
- optional local archive index, catalog, note, or record references

## Writes

- proposed or confirmed final PDF path
- optional updated archive references when the workflow explicitly includes them
- optional index or catalog updates after explicit confirmation
- duplicate findings and move status

## Source Of Truth

- stable `bibkey`
- current local archive conventions
- provided paper metadata
- duplicate evidence from existing files, notes, records, and indexes

## Required Behavior

- inspect the local archive structure before moving
- keep the current stable filename unless the task explicitly re-invokes rename work
- detect duplicate risk using `bibkey`, title, and DOI evidence where available
- preview the final path before executing the move
- stop on likely duplicate conflicts instead of guessing which copy is canonical
- update related indexes or note references only on confirmed execution

## Non-Goals

- generating bibkeys
- renaming PDFs
- writing notes
- rewriting bibliography metadata
- creating a new note if one does not exist

## Output Contract

Report at least:

- source path
- proposed final path
- duplicate status
- whether a move is required
- whether the move is safe to execute

## Overview

Use this skill to archive a paper PDF into its final place in the current workspace or library.

This skill assumes the paper already has a stable `bibkey` and a usable filename.

It decides:

- where the PDF should live
- whether the move is safe
- whether the index should be updated
- whether the paper appears to duplicate an existing library item

Default workflow: preview first, execute only after explicit confirmation.

## Responsibilities

- Decide the final attachment path from provided metadata and discovered local structure rules.
- Move the PDF into the final archive location after confirmation.
- Update the local paper index or catalog when one exists.
- Update direct attachment references inside an existing note or record when one exists.
- Detect likely duplicate papers before any move or index write.

Do not:

- invent or repair bibkeys
- rename PDFs
- generate `short_title_zh`
- create a new paper summary note
- write paper summaries, key points, or quote blocks
- rewrite `.bib` content

## Input Contract

Default inputs may include:

- one already-keyed PDF or a small batch of PDFs
- metadata such as `bibkey`, `title`, `year`, `doi`, and `area`
- an optional note or record path

The skill should treat the local workspace's existing structure as a constraint, not as a blank design exercise.

## Archive Rules

- First inspect how the current workspace already stores papers, attachments, notes, and indexes.
- Use the provided `area` as the authority for the paper's primary home when the workspace already has an `area`-like convention.
- By default, materialize only the first path segment of a hierarchical `area` value in the physical attachment path.
- If the workspace already uses a different stable convention, preserve that convention instead of forcing a new one.
- If `area` is missing or unreliable and no stronger local convention exists, place the PDF in a neutral fallback bucket such as `_unsorted` under the discovered paper-attachment root.
- Do not duplicate the same PDF across multiple topic folders.
- Express multi-topic relationships through notes, metadata, tags, catalogs, or navigation pages instead of extra copies.

## Index And Reference Sync

On confirmed execution, update:

- the local paper index or catalog, if present
- the existing note or record, if present

For the index or catalog:

- discover the existing grouped style from local files before editing
- append or update the entry under the matching section when a stable grouping scheme already exists
- do not create a separate machine-generated dump section

For the note or record:

- update frontmatter `source:`
- update direct file links in the body when present

Do not:

- rewrite the note title
- rename the note file
- create a new note if one does not exist

## Duplicate Detection

Check duplicates before moving anything.

Use combined evidence:

- `bibkey`
- `title`
- `doi`

Default behavior on duplicate detection:

- stop the archive action
- do not move the PDF
- do not update the index or catalog
- do not update the note or record
- report the duplicate evidence and suggested next action

## Workflow

1. Inspect the target PDF and provided metadata.
   Confirm that a stable `bibkey` already exists.
   If the bibkey is missing or clearly unstable, defer to `$paper-bibkey`.

2. Resolve the primary archive bucket.
   Discover the existing attachment root and archive pattern first.
   Use `area` when provided and compatible with the existing pattern.
   Fall back to a neutral unsorted bucket when the metadata is not trustworthy and the workspace offers no better rule.

3. Check the current library for duplicates.
   Search existing attachment paths, notes or records, and index entries using `bibkey`, title, and DOI.
   Stop if the paper appears to already exist.

4. Build the final path.
   Keep the current stable filename.
   Only change the parent directory unless the user explicitly coupled this task with `$paper-rename`.

5. Preview the operation.
   Show the final path, whether the move is required, whether the local index will change, whether the related note will change, and whether duplicates were found.

6. Execute only on explicit confirmation.
   Move the PDF.
   Update the local index or catalog when one exists.
   Update the related note attachment references when a note exists.

## Output Discipline

- Prefer the smallest archive move that makes the library consistent.
- Keep the physical directory tree shallow by materializing only the primary topic bucket.
- Stop on duplicates instead of guessing which copy is canonical.
- If the main task is identifying which paper a PDF is or whether it already exists locally, use `$paper-match`.
- If the main task is generating or repairing the key, use `$paper-bibkey`.
- If the main task is normalizing the filename, use `$paper-rename`.
- If the main task is writing or updating the paper note body, use `$paper-notes`.
- If the main task is batch bibliography reconciliation or duplicate-oriented library status, use `$paper-reconcile`.
- If the main task is maintaining the missing-paper checklist, use `$paper-missing`.

## Commands

Prefer fast local inspection:

- List current paper attachments: `rg --files <workspace-root> | rg "\\.pdf$"`
- Search direct PDF references: `rg -n "source:|\\.pdf" <workspace-root>`
- Search duplicate bibkeys or titles: `rg -n "<bibkey>|<title>|<doi>" <workspace-root>`
- Inspect local metadata fields: `rg -n "^area:|^source:|^bibkey:|^year:|^doi:" <workspace-root>`
