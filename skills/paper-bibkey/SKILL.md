---
name: paper-bibkey
description: Generate or repair a stable BibTeX key for a paper using the canonical pattern `firstauthor_YYYY_shorttopic`, preview the proposed key, and keep the final identifier ASCII, short, and repeatable.
---

# Paper BibKey

## Purpose

Create or repair a stable canonical bibkey for a paper after its identity is known.

## Reads

- matched paper metadata
- optional bibliography entries
- optional notes or local records that already mention a bibkey

## Writes

- the chosen bibkey proposal
- optional `.bib` key updates when the broader workflow explicitly applies them

## Source Of Truth

- confirmed paper identity
- first author surname
- publication year
- one or two short English topic words

## Required Behavior

- use `firstauthor_YYYY_shorttopic`
- keep the key lowercase ASCII with underscores
- prefer stability over stylistic churn
- keep an already good key when it is not causing real workflow pain
- report collisions explicitly instead of silently appending arbitrary suffixes

## Non-Goals

- matching a PDF to its paper identity
- renaming PDFs
- deciding archive layout
- writing notes

## Output Contract

Report at least:

- current key if any
- proposed key
- rationale
- collision status
- stable alternatives when the first candidate conflicts
