---
name: paper-organize
description: Move an already-keyed and already-renamed paper PDF into its final archive location, report duplicate risk before moving, and align the file with the local archive structure without changing bibliography semantics.
---

# Paper Organize

## Purpose

Place a paper PDF into its final archive location after identity and filename are already stable.

## Reads

- PDF path
- confirmed bibkey
- optional domain or topic metadata
- optional local archive index or note references

## Writes

- final PDF path
- optional updated archive references when the workflow explicitly includes them

## Source Of Truth

- stable bibkey
- current local archive conventions
- duplicate evidence from existing files and records

## Required Behavior

- inspect the local archive structure before moving
- keep the current stable filename unless the task explicitly re-invokes rename work
- detect duplicate risk using bibkey, title, and DOI evidence where available
- preview the final path before executing the move
- stop on likely duplicate conflicts instead of guessing which copy is canonical

## Non-Goals

- generating bibkeys
- renaming PDFs
- writing notes
- rewriting bibliography metadata

## Output Contract

Report at least:

- source path
- proposed final path
- duplicate status
- whether a move is required
- whether the move is safe to execute
