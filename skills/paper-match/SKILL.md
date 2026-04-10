---
name: paper-match
description: Match local paper PDFs to known paper identities by recovering title, authors, year, DOI, venue, and first-page evidence, then report confidence, ambiguity, and duplicate risk before downstream bibkey, rename, organize, or note-writing steps.
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

## Source Of Truth

- the PDF itself and its recoverable first-page evidence
- trusted bibliography metadata when present
- DOI and exact title evidence as the strongest identity signals

## Required Behavior

- recover identity evidence conservatively instead of trusting noisy filenames
- distinguish confident matches, ambiguous matches, and unmatched cases
- detect duplicate risk before downstream rename or organize work
- prefer exact title and DOI evidence when available
- use `references/matching-evidence.md` as the decision baseline
- use `scripts/collect_signals.py` when a quick local evidence dump would help

## Non-Goals

- generating or repairing bibkeys
- renaming PDFs
- deciding final archive placement
- writing paper notes
- collection-level reconciliation

## Output Contract

Report at least:

- target PDF path
- recovered evidence
- best match candidate
- confidence level
- duplicate suspicion
- blockers or ambiguities
- whether downstream steps can proceed safely
