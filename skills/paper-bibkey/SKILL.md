---
name: paper-bibkey
description: Generate or repair stable BibTeX keys for papers using the `firstauthor_YYYY_shorttopic` pattern, preview the proposed key and any `.bib` changes first, then update the target `.bib` entry or create a minimal stub entry on confirmation. Use when Codex needs to assign a bibkey to a paper PDF, metadata note, or BibTeX entry, check whether an existing key should be kept, resolve bibkey conflicts by offering stable alternatives, or synchronize the chosen `bibkey:` into an existing paper record.
---

# Paper BibKey

## Purpose

Create or repair a stable canonical bibkey for a paper after its identity is known, using the `firstauthor_YYYY_shorttopic` pattern while preserving stable existing keys whenever possible.

## Reads

- confirmed or strongly supported paper identity metadata
- target `.bib` entries or the destination bibliography file
- optional notes or local records that already mention `bibkey:`
- optional PDF metadata or first-page text when identity support is still needed

## Writes

- the proposed bibkey and conflict analysis
- optional `.bib` entry-key updates after explicit confirmation
- optional minimal BibTeX stub entries after explicit confirmation
- optional `bibkey:` updates inside an existing metadata note or paper record

## Source Of Truth

- confirmed paper identity
- first author surname
- publication year
- one or two short English topic words that distinguish the paper
- exact collision checks against the target `.bib`

## Required Behavior

- preview the proposed key and downstream `.bib` or note changes before writing
- use `firstauthor_YYYY_shorttopic`
- keep the key lowercase ASCII with underscores
- prefer stability over stylistic churn
- keep an already good key when it is not causing real workflow pain
- report collisions explicitly instead of silently appending arbitrary suffixes
- create a minimal stub entry only when the paper lacks a corresponding `.bib` entry and the user confirms
- sync only `bibkey:` into an existing note or record unless the user asked for broader edits

## Non-Goals

- matching a PDF to its paper identity
- renaming PDFs or other attachments
- deciding archive layout
- generating `short_title_zh`
- rewriting note titles or note filenames
- writing or rewriting note bodies
- mass-editing unrelated `.bib` entries

## Output Contract

Report at least:

- source paper
- current key if any
- proposed key
- rationale
- collision status
- whether the `.bib` entry will be updated or a stub entry will be created
- whether an existing metadata note's `bibkey:` will be updated
- stable alternatives when the first candidate conflicts

## Overview

Use this skill to generate and stabilize the internal BibTeX key for a paper.

Default target format:

`firstauthor_YYYY_shorttopic`

Where:

- `firstauthor` is the ASCII-normalized surname of the first author.
- `YYYY` is the publication year.
- `shorttopic` is 1 to 2 short English topic words.

Preview first. Update `.bib` and note metadata only after the user explicitly confirms.

## Responsibilities

- Generate a stable candidate bibkey for a paper PDF, metadata note, or existing `.bib` entry.
- Reuse an existing good key when it is already stable and appropriate.
- Replace a bad or noisy key only after preview and confirmation.
- Create a minimal BibTeX stub entry when the paper has no corresponding `.bib` entry yet.
- Sync the chosen `bibkey:` into an existing metadata note or paper record when one exists.

Do not:

- rename PDFs or other attachments
- generate `short_title_zh`
- rewrite note titles or note filenames
- rewrite citation prose blocks just because the bibkey changed
- mass-edit unrelated `.bib` entries

## Workflow

1. Inspect the input scope.
   Accept a single PDF, a single metadata note, a single `.bib` entry, or a small batch.
   Locate the target `.bib` file, the corresponding metadata note if present, and the source paper metadata.

2. Resolve the paper identity conservatively.
   Use title, authors, year, DOI, venue, first-page text, and user-provided mapping as available.
   If confidence is low, stop and report the ambiguity.

3. Check for an existing bibkey.
   If the current key is already stable and follows the local naming conventions closely enough, keep it.
   If the current key is missing, noisy, or clearly unhelpful, propose a replacement.

4. Generate the candidate bibkey.
   Build `firstauthor_YYYY_shorttopic` from:
   - first-author surname
   - publication year
   - 1 to 2 English topic words that distinguish the paper
   Normalize to lowercase ASCII with underscores.
   Avoid copying the whole title into the key.

5. Check for conflicts.
   Search the target `.bib` for exact-key collisions.
   If the candidate conflicts with a different paper, stop and offer 1 to 3 stable alternatives.
   Do not silently append arbitrary numeric suffixes.

6. Preview the intended changes.
   Show:
   - source paper
   - current key if any
   - proposed key
   - naming rationale
   - conflict status
   - whether the `.bib` entry will be updated or a stub entry will be created
   - whether an existing metadata note's `bibkey:` will be updated

7. Execute only on explicit confirmation.
   For an existing `.bib` entry, update only the entry key unless the user asked for more.
   For a missing entry, create a minimal stub entry with the recoverable fields.
   If a corresponding metadata note exists, write or update:
   - `bibkey: ...`

## Key Rules

- Prefer stability over perfect style purity.
- Keep a good existing key rather than renaming it just to be more elegant.
- Use the first author's surname as the anchor, not the most famous later author.
- Keep `shorttopic` short, concrete, and distinguishable.
- Prefer workspace searchability and repeatability over clever abbreviations.

## Stub Entry Rules

- Use the closest BibTeX type that can be supported confidently, usually `@article`, `@inproceedings`, or `@misc`.
- Fill only fields that can be recovered with reasonable confidence, such as `title`, `author`, `year`, `doi`, `url`, `journal`, or `booktitle`.
- Leave missing fields absent rather than inventing them.

## Output Discipline

- Always preview before writing.
- Keep bibkeys lowercase ASCII with underscores.
- Report conflicts explicitly and provide stable alternatives.
- Sync only `bibkey:` into the related metadata note in v1.
- If the main task is identifying which paper a PDF is or whether it duplicates an existing record, use `$paper-match`.
- If the main task is deciding the final archive location and moving the PDF, use `$paper-organize`.
- If the main task is renaming PDFs to consume an existing bibkey, use `$paper-rename`.
- If the main task is writing or updating the paper note body, use `$paper-notes`.
- If the main task is batch bibliography reconciliation or duplicate-oriented library status, use `$paper-reconcile`.
- If the main task is maintaining the missing-paper checklist, use `$paper-missing`.

## Commands

Prefer fast local inspection:

- Search existing keys: `rg -n "^@(article|inproceedings|misc)\\{" <bibfile>`
- Search a specific key: `rg -n "@[A-Za-z]+\\{<candidate-key>," <bibfile>`
- Read PDF metadata: `pdfinfo <file.pdf>`
- Extract first page text: `pdftotext -f 1 -l 1 -nopgbrk -layout <file.pdf> -`
- Search local metadata notes: `rg -n "^bibkey:|^source:|^author:|^year:" <workspace-root>`
