---
name: paper-reconcile
description: Reconcile a paper bibliography against the current local library at the collection level, maintain matched and unmatched coverage status, and track duplicate-oriented library state without redoing per-paper identity resolution. Use when Codex needs a batch view of which bibliography entries are covered, uncovered, or duplicated across local PDFs and records. If the main task is matching a specific PDF to its paper identity, use `paper-match`; if the main task is updating the missing-paper checklist itself, use `paper-missing`.
---

# Paper Reconcile

## Purpose

Maintain the collection-level picture of a paper library.

## Reads

- one or more bibliography files
- local PDFs
- local notes, records, indexes, or catalogs
- optional precomputed match results

## Writes

- collection-level reconciliation summary
- optional updated coverage records when the broader workflow explicitly maintains them
- duplicate-oriented findings or clusters

## Source Of Truth

- bibliography scope
- reliable local coverage evidence
- confirmed per-paper match results when available

## Required Behavior

- compare expected bibliography entries against local coverage
- reuse confirmed per-paper match results instead of re-matching from scratch
- maintain matched, unmatched, and duplicate-oriented status
- keep ambiguous cases explicit instead of force-classifying them
- hand checklist refresh work off conceptually to `paper-missing` when that is the real task

## Non-Goals

- per-paper identity matching as the main task
- bibkey generation
- filename normalization
- archive placement
- note writing
- editing the missing-paper checklist itself
- rewriting `.bib` content unless the user explicitly expands the task

## Output Contract

Report at least:

- matched entries
- unmatched entries
- duplicate-oriented findings or clusters
- summary counts or coverage ratios
- whether the current local state is sufficient for downstream missing-list refreshes

## Overview

Use this skill to maintain the collection-level picture of a paper library.

This skill is for batch reconciliation and duplicate-oriented status, not for per-paper identity resolution, bibkey repair, filename normalization, archive placement, note writing, or missing-checklist editing.

## Responsibilities

- Read one or more `.bib` files and define the expected paper set.
- Compare that expected set against local PDFs, notes, records, or existing indexes.
- Reuse confirmed results from `$paper-match` instead of re-matching a specific paper from scratch.
- Maintain matched, unmatched, and duplicate-oriented collection status.
- Report coverage summaries and duplicate clusters clearly.

Do not:

- perform per-paper identity matching from scratch when that is the main task
- generate or repair bibkeys
- rename PDFs
- decide archive placement
- write paper note bodies
- edit the missing-paper checklist itself
- rewrite `.bib` content unless the user explicitly expands the task

## Input Contract

Default inputs may include:

- one or more `.bib` files
- local PDFs
- metadata notes or records
- existing library indexes or catalogs
- optional precomputed match results from `$paper-match`

## Workflow

1. Read the bibliography and define scope.
   Separate genuine paper entries from non-paper material when needed.

2. Inspect the local paper library.
   Scan PDFs, notes, records, or existing indexes that represent local paper coverage.

3. Reuse confirmed paper identity results.
   Prefer existing outputs from `$paper-match` when available.
   If a specific PDF still needs identity resolution, hand that step off to `$paper-match` instead of guessing here.

4. Reconcile collection coverage.
   Determine which bibliography entries are confidently covered, which are still uncovered, and which local artifacts look redundant.

5. Report duplicate-oriented status.
   Group likely duplicate downloads or duplicate records conservatively and keep ambiguous cases explicit.

6. Hand off checklist maintenance when needed.
   If the user wants the missing-paper checklist itself refreshed, send that step to `$paper-missing`.

## Reconciliation Rules

- Prefer confirmed per-paper match results over ad hoc re-matching inside this skill.
- Keep ambiguous cases explicit instead of force-classifying them as covered.
- Treat duplicate detection as collection status, not as a request to delete files automatically.
- Preserve stable local records unless the user explicitly asks for broader cleanup.

## Output Discipline

- Keep collection-level reconciliation separate from single-paper processing.
- If the main task is determining which specific paper a PDF is, use `$paper-match`.
- If the main task is updating the missing-paper checklist itself, use `$paper-missing`.
- If the main task is generating or repairing a bibkey, use `$paper-bibkey`.
- If the main task is normalizing a PDF filename, use `$paper-rename`.
- If the main task is deciding archive placement, use `$paper-organize`.
- If the main task is writing the paper note body, use `$paper-notes`.

## Commands

Prefer fast local inspection:

- Search bibliography entries: `rg -n "^@(article|inproceedings|misc)\\{" <bibfile>`
- Search local paper evidence: `rg -n "bibkey:|doi:|source:|\\.pdf" <workspace-root>`
- Search duplicate evidence: `rg -n "<bibkey>|<title>|<doi>" <workspace-root>`
- Search existing indexes or catalogs: `rg -n "matched|unmatched|duplicate|coverage|missing" <workspace-root>`
