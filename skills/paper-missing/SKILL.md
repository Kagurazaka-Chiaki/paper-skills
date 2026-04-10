---
name: paper-missing
description: Maintain missing-paper checklists for a local paper library by comparing expected bibliography entries against what is already present, updating missing and newly-found status, and keeping the missing-paper summary accurate. Use when Codex needs to track which papers from a bibliography are still absent, refresh a missing-paper list after new downloads or matches, or separate still-missing items from already-covered items without doing per-paper note writing or archive work.
---

# Paper Missing

## Purpose

Maintain the still-missing view of a paper collection.

## Reads

- one or more `.bib` files
- an existing missing-paper checklist
- local PDFs, metadata records, notes, or indexes
- optional precomputed match results from `$paper-match`

## Writes

- updated missing-paper checklist
- updated missing counts or newly-covered summaries when the local format supports them
- a conservative status report of still-missing, newly covered, and unresolved items

## Source Of Truth

- the expected paper set defined by the bibliography
- reliable evidence that a paper is already present locally
- confirmed match results when they exist
- existing user-maintained checklist annotations that are still valid

## Required Behavior

- compare the expected paper set against current local coverage
- remove newly covered papers conservatively
- keep unresolved or ambiguous cases in the missing set
- preserve user-maintained annotations unless they are clearly obsolete
- separate still-missing, newly covered, and unresolved items in the report

## Non-Goals

- per-paper identity matching as the main task
- bibkey generation or repair
- filename normalization
- archive placement
- note writing

## Output Contract

Report at least:

- entries still missing
- entries newly covered
- whether the checklist changed
- the updated missing count

## Overview

Use this skill to maintain the "still missing" view of a paper collection.

This skill is for checklist maintenance and status updates, not for per-paper identity resolution, note writing, or archive placement.

## Responsibilities

- Compare the expected bibliography against what is already present locally.
- Identify which papers are still missing.
- Remove newly covered papers from missing lists.
- Keep numeric missing-paper summaries accurate.
- Preserve a clear record of what remains missing versus what is now covered.

Do not:

- perform per-paper identity matching from scratch when that is the main task
- generate or repair bibkeys
- rename PDFs
- decide archive placement
- write paper note bodies

## Input Contract

Default inputs may include:

- one or more `.bib` files
- an existing missing-paper checklist
- local PDFs, metadata records, or notes
- optional precomputed match results from `$paper-match`

## Missing Rules

- Prefer confirmed per-paper match results when they already exist.
- Treat a paper as covered when there is reliable evidence that it is already present locally.
- Keep unresolved or ambiguous cases in the missing set rather than over-removing them.
- Preserve user-maintained annotations in the missing list unless they are clearly obsolete.

## Workflow

1. Read the bibliography and define the expected paper set.
   Separate genuine paper entries from non-paper material when needed.

2. Read the current missing-paper checklist if one exists.
   Preserve the existing structure when it is already usable.

3. Determine local coverage.
   Reuse confirmed results from `$paper-match` when available.
   Otherwise use existing bibliography status, local metadata, PDFs, or notes as evidence of presence.

4. Refresh the checklist.
   Remove entries that are now confidently covered.
   Keep entries that are still absent or still ambiguous.
   Update summary counts and any "newly found" view if the local format supports it.

5. Report the result clearly.
   Distinguish still-missing items, newly covered items, and unresolved ambiguous items.

## Output Discipline

- Prefer conservative checklist updates over optimistic removal.
- If the main task is determining which specific paper a PDF is, use `$paper-match`.
- If the main task is library-wide reconciliation beyond the missing list itself, use `$paper-reconcile`.
- If the main task is generating or repairing a bibkey, use `$paper-bibkey`.
- If the main task is normalizing the filename, use `$paper-rename`.
- If the main task is archive placement, use `$paper-organize`.
- If the main task is writing the paper note body, use `$paper-notes`.

## Commands

Prefer fast local inspection:

- Search bibliography entries: `rg -n "^@(article|inproceedings|misc)\\{" <bibfile>`
- Search local coverage evidence: `rg -n "bibkey:|doi:|source:|\\.pdf" <workspace-root>`
- Search existing missing lists: `rg -n "missing|todo|not found|未下载|缺失" <workspace-root>`
