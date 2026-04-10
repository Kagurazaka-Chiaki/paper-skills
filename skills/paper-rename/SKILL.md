---
name: paper-rename
description: Normalize noisy manually downloaded paper PDF filenames into `{bibkey} - {中文短标题}.pdf`, using an existing BibTeX key or explicit mapping as the stable input key. Use when Codex needs to preview or execute paper PDF renames, compress a readable Chinese short title, reuse stable `bibkey` and `short_title_zh` metadata in existing notes or records, or synchronize direct references after a PDF rename. If the main task is generating or repairing the bibkey itself, use `paper-bibkey` first; if the main task is deciding the final archive location and moving the paper into the library, use `paper-organize` instead.
---

# Paper Rename

## Purpose

Normalize noisy paper PDF filenames after paper identity and bibkey are already known.

## Reads

- PDF path
- confirmed `bibkey`
- optional short display title
- optional local notes or metadata that already contain a stable display title
- optional `.bib` data or explicit mappings

## Writes

- renamed PDF path
- optional updated path references in user-managed records when the workflow explicitly includes them
- optional `bibkey:` and `short_title_zh:` metadata updates in related notes or records

## Source Of Truth

- confirmed `bibkey`
- display-oriented short title
- local filesystem constraints such as illegal filename characters
- stable note or record metadata when present

## Required Behavior

- use `{bibkey} - {short_title}.pdf`
- keep `bibkey` unchanged and ASCII-only
- treat `short_title` as display text rather than an internal key
- strip illegal filename characters and trailing dots or spaces
- preview the target name before executing the rename
- stop on path conflicts instead of inventing fallback names automatically
- sync direct references after a confirmed rename

## Non-Goals

- creating the bibkey itself
- deciding the final archive directory
- writing note bodies
- using `.bib` as workflow state
- renaming paper-note Markdown filenames

## Output Contract

Report at least:

- source path
- resolved bibkey
- resolved short title
- target filename
- conflict status
- whether the rename is safe to execute

## Overview

Use this skill to clean up unstable paper PDF filenames without assuming any specific repository layout or note platform.

Target filename format:

`{bibkey} - {中文短标题}.pdf`

Where:

- `bibkey` is the internal stable key and stays ASCII.
- `中文短标题` is for display density only and should usually fit within about 8 to 14 Chinese characters.
- The rename should be previewed first and executed only after the user explicitly asks for it.

## Responsibilities

- Read existing `.bib` data, note metadata, or an explicit mapping and prefer the existing `bibkey`.
- Compress a Chinese short title from the paper content or an existing note or record instead of copying the full English title.
- Reuse stable note metadata when it already exists so repeated runs do not churn filenames.
- Sync direct Markdown references after a confirmed rename.

Do not:

- rewrite `.bib` content unless the user explicitly asks
- rename paper-note Markdown filenames
- rewrite note titles just because the PDF filename changed
- bulk-edit unrelated notes, indexes, or project files

## Workflow

1. Inspect the target scope.
   Accept a single PDF or a paper directory.
   List PDFs, existing notes or metadata records, and any `.bib` file or explicit mapping the user provided.

2. Resolve the paper identity conservatively.
   Prefer exact BibTeX title matches.
   Confirm with author names, year, DOI, venue, or first-page text when needed.
   If confidence is low, stop and report the ambiguity instead of forcing a rename.

3. Resolve `bibkey`.
   Prefer an existing BibTeX key exactly as written.
   If a matching note or metadata record already has `bibkey:` in frontmatter, reuse it.
   If no stable key exists, stop and direct the task to `$paper-bibkey` instead of inventing a new key here.

4. Resolve `short_title_zh`.
   Prefer an existing note or metadata record's `short_title_zh:` value when present.
   Otherwise derive a concise Chinese short title from the paper's problem, method, or distinguishing phrase.
   Keep it informative but compact, usually 8 to 14 Chinese characters.
   Compress aggressively when needed instead of transliterating the full English title.

5. Sanitize the target filename.
   Remove Windows-illegal characters: `<>:"/\\|?*`.
   Remove trailing spaces and trailing dots.
   Preserve the original `bibkey` spelling.

6. Preview before mutating.
   Show:
   - source PDF path
   - resolved or suggested `bibkey`
   - resolved or proposed `short_title_zh`
   - target filename
   - whether the rename is safe, ambiguous, or blocked by conflict

7. Execute only on explicit user confirmation.
   Rename the PDF only when the target filename is conflict-free.
   If the target filename already exists and is not the same file, stop and report the conflict.

8. Sync stable metadata and direct references.
   If a corresponding note or metadata record exists, store or update:
   - `bibkey: ...`
   - `short_title_zh: ...`
   Update direct references that point to the renamed PDF, at minimum:
   - note frontmatter `source:`
   - explicit file links inside related notes
   - explicit links in local index pages or catalogs when they exist

## Matching Rules

- Prefer title-based matching over filename guesses.
- Use note or record metadata as a stable source when present.
- Use PDF metadata only as a helper, not as the sole source of truth.
- If the PDF is a proceedings volume, locate the actual paper before assigning a `bibkey`.
- If the user gives an explicit mapping, trust it over heuristic matching.

## Short Title Rules

- Prefer semantic compression over literal translation.
- Keep only the phrase that best distinguishes the paper in the current library.
- Avoid filler words such as “一种方法”, “研究”, “论文”, or “基于” unless they are essential for disambiguation.
- Avoid illegal filename characters and punctuation that adds length without meaning.
- When two candidate short titles are similarly good, prefer the shorter one.

## Output Discipline

- Always preview before executing a rename.
- Keep `bibkey` ASCII-only and stable across reruns.
- Treat `short_title_zh` as display metadata rather than an internal key.
- Keep metadata and direct references synchronized after a confirmed rename.
- If the main task is identifying which paper a PDF is, use `$paper-match` first.
- If the bibkey is missing, noisy, or needs replacement, use `$paper-bibkey` first.
- If the main task is deciding the final archive location and moving the paper into the library, use `$paper-organize`.
- If the main task is writing or updating the paper note body, use `$paper-notes`.
- If the main task is library-wide Bib reconciliation or duplicate-oriented library status rather than filename cleanup, prefer `$paper-reconcile`.
- If the main task is maintaining the missing-paper checklist, prefer `$paper-missing`.

## Commands

Prefer fast local inspection:

- List PDFs: `Get-ChildItem <paper-dir> -Filter *.pdf`
- Search BibTeX keys: `rg -n "^@(article|inproceedings|misc)\\{" <bibfile>`
- Read PDF metadata: `pdfinfo <file.pdf>`
- Extract first page text: `pdftotext -f 1 -l 1 -nopgbrk -layout <file.pdf> -`
- Search direct PDF references: `rg -n "<old-pdf-name>|source:" <workspace-root>`
