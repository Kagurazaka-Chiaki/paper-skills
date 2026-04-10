---
name: paper-notes
description: Create or update a structured paper note from an already-identified paper, using a stable bibkey, known metadata, and a provided note path, while staying faithful to the source paper instead of inventing missing detail.
---

# Paper Notes

## Purpose

Create or update the content of a paper note after the paper identity is already settled.

## Reads

- one paper PDF
- a stable bibkey
- paper metadata such as title, authors, venue, year, DOI, URL, and source path
- a provided note path
- optional existing note content

## Writes

- created or updated note content at the provided path
- optional note metadata refinements when supported by the inputs

## Source Of Truth

- the identified paper PDF
- known metadata
- existing good note content when present

## Required Behavior

- create a structured note instead of a loose text dump
- preserve good existing content unless the user asked for a rewrite
- fill missing sections before rewriting strong sections
- stay faithful to the paper and known metadata
- write a narrower partial note when extraction quality is weak instead of inventing detail

## Non-Goals

- matching the PDF to a BibTeX entry
- inventing or repairing the bibkey
- renaming the PDF
- deciding the archive path
- choosing the note path

## Output Contract

Report at least:

- whether the note was created or updated
- whether existing metadata was reused
- whether the note is complete or intentionally partial
- which sections remain narrow because the source material was weak
