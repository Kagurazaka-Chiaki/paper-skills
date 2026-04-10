---
name: paper-rename
description: Rename a paper PDF into the canonical display format `{bibkey} - {short_title}.pdf` after the bibkey is already settled, keeping the bibkey ASCII and the display title compact.
---

# Paper Rename

## Purpose

Normalize noisy paper PDF filenames after paper identity and bibkey are already known.

## Reads

- PDF path
- confirmed bibkey
- optional short display title
- optional local notes or metadata that already contain a stable display title

## Writes

- renamed PDF path
- optional updated path references in user-managed records when the workflow explicitly includes them

## Source Of Truth

- confirmed bibkey
- display-oriented short title
- local filesystem constraints such as illegal filename characters

## Required Behavior

- use `{bibkey} - {short_title}.pdf`
- keep `bibkey` unchanged and ASCII-only
- treat `short_title` as display text rather than an internal key
- strip illegal filename characters and trailing dots or spaces
- preview the target name before executing the rename
- stop on path conflicts instead of inventing fallback names automatically

## Non-Goals

- creating the bibkey itself
- deciding the final archive directory
- writing note bodies
- using `.bib` as workflow state

## Output Contract

Report at least:

- source path
- resolved bibkey
- resolved short title
- target filename
- conflict status
- whether the rename is safe to execute
