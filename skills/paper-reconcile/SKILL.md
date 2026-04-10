---
name: paper-reconcile
description: Reconcile a paper bibliography against the current local library at the collection level, maintain matched and unmatched coverage, and report duplicate-oriented status without redoing per-paper identity resolution.
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

## Output Contract

Report at least:

- matched entries
- unmatched entries
- duplicate-oriented findings or clusters
- summary counts or coverage ratios
