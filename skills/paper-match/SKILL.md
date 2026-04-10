---
name: paper-match
description: Match one or more local paper PDFs to existing BibTeX entries or metadata records, identify likely duplicates, and report confident or ambiguous matches before any downstream note-writing or archive steps. Use when Codex needs to determine which paper a PDF actually is, decide whether it already exists in the local library, reconcile PDFs against a `.bib` file, or hand a confirmed paper identity to later skills such as `paper-bibkey`, `paper-rename`, `paper-organize`, or `paper-notes`.
---

# Paper Match

## Purpose

Identify what a local paper PDF actually is before downstream normalization or archive work begins.

## Reads

- one PDF or a small batch of PDFs
- optional `.bib` files
- optional local notes, indexes, or metadata records
- optional user hints such as title, author, year, DOI, or venue
- optional bundled resources under `templates/`, `scripts/`, and `references/`

## Writes

- no mandatory repository writes
- optional structured match report based on `templates/match-report-template.md`
- a clean handoff record for downstream skills

## Source Of Truth

- the PDF itself and its recoverable first-page evidence
- trusted bibliography metadata when present
- DOI and exact title evidence as the strongest identity signals
- duplicate evidence across local PDFs, notes, indexes, and `.bib` entries

## Required Behavior

- recover identity evidence conservatively instead of trusting noisy filenames
- distinguish confident matches, ambiguous matches, and unmatched cases
- detect duplicate risk before downstream rename or organize work
- prefer exact title and DOI evidence when available
- use `references/matching-evidence.md` as the decision baseline
- use `scripts/collect_signals.py` when a quick local evidence dump would help
- stop on unresolved ambiguity instead of forcing a match

## Non-Goals

- generating or repairing bibkeys
- renaming PDFs
- deciding final archive placement
- writing paper notes
- collection-level reconciliation
- rewriting `.bib` content unless the user explicitly expands the task

## Output Contract

For each target PDF, report at least:

- target PDF path
- recovered evidence
- best match candidate
- confidence level
- duplicate suspicion
- blockers or ambiguities
- whether downstream steps can proceed safely

## Overview

Use this skill to determine which paper a local PDF corresponds to.

This skill is responsible for identity resolution, not for renaming, archive placement, bibkey repair, or note writing.

Default goal:

- match a PDF to the correct BibTeX entry or metadata record
- detect whether the paper is already represented locally
- report the confidence and any ambiguity before downstream steps begin

## Responsibilities

- Inspect a paper PDF and recover enough evidence to identify it.
- Match the PDF to an existing `.bib` entry or metadata record when possible.
- Detect likely duplicates across local PDFs, notes, indexes, or `.bib` entries.
- Distinguish confident matches from ambiguous or unresolved cases.
- Produce a clean handoff record for later steps.

Do not:

- invent or repair the `bibkey`
- rename the PDF
- choose the final archive path
- write the paper note body
- rewrite `.bib` content unless the user explicitly expands the task

## Input Contract

Default inputs may include:

- one PDF or a small batch of PDFs
- an optional `.bib` file
- optional local metadata records or notes
- optional explicit hints such as title, author, year, DOI, or venue

The skill should work even when filenames are noisy.

## Matching Rules

- Match by title first when a reliable title can be recovered.
- Confirm with author names, year, DOI, venue, or first-page text when possible.
- Use PDF metadata as a helper, not as the sole source of truth.
- If the PDF is a proceedings or collected volume, locate the actual paper before deciding the match.
- If multiple candidates remain plausible, stop and report the ambiguity instead of forcing a match.

## Duplicate Rules

- Treat an exact BibTeX-key collision as strong duplicate evidence.
- Treat DOI equality as strong duplicate evidence.
- Treat exact or near-exact title matches plus author/year agreement as likely duplicate evidence.
- Report duplicates before any downstream rename, organize, or note-writing step.

## Workflow

1. Inspect the target PDFs.
   Ignore noisy filenames as identity evidence unless nothing stronger exists.
   Recover title, author, year, DOI, venue, and first-page text where possible.

2. Scan the local bibliography and metadata.
   Search `.bib` entries, local metadata notes, and any existing paper catalogs or indexes.

3. Produce match candidates.
   Prefer exact title matches.
   Use authors, year, venue, and DOI to separate near matches.

4. Assess confidence.
   Mark the result as confident, ambiguous, or unmatched.
   Stop on ambiguity rather than guessing.

5. Check for duplicates.
   Search for the same paper under different filenames, locations, or records.
   Report the duplicate evidence and whether the incoming PDF appears redundant.

6. Hand off the result.
   If the paper identity is confirmed but the bibkey is missing or bad, send the next step to `$paper-bibkey`.
   If the paper is identified and already keyed, send later filename work to `$paper-rename`, archive work to `$paper-organize`, and note writing to `$paper-notes`.

## Output Discipline

- Prefer a narrower but reliable match over an overconfident guess.
- Keep unmatched and ambiguous cases explicit.
- If the main task is batch bibliography reconciliation or duplicate-oriented library status, use `$paper-reconcile`.
- If the main task is maintaining the missing-paper checklist, use `$paper-missing`.
- If the main task is generating or repairing the `bibkey`, use `$paper-bibkey`.
- If the main task is normalizing the filename after the match is known, use `$paper-rename`.
- If the main task is archive placement after the match is known, use `$paper-organize`.
- If the main task is writing the paper note after the match is known, use `$paper-notes`.

## Commands

Prefer fast local inspection:

- Search bibliography entries: `rg -n "^@(article|inproceedings|misc)\\{" <bibfile>`
- Read PDF metadata: `pdfinfo <file.pdf>`
- Extract first page text: `pdftotext -f 1 -l 1 -nopgbrk -layout <file.pdf> -`
- Search local references: `rg -n "<title>|<doi>|<author>|<year>" <workspace-root>`
- Collect matching signals quickly: `python scripts/collect_signals.py`
