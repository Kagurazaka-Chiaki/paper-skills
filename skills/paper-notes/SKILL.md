---
name: paper-notes
description: Create or update a paper note from an already-identified paper, using an existing PDF path, stable bibkey, known metadata, and a provided note path. Use when Codex needs to write a complete reading note, enrich an existing note with structured sections, or turn recovered paper metadata and PDF content into a faithful note body. This skill does not match PDFs to BibTeX, repair bibkeys, rename files, choose archive paths, or decide the note path itself.
---

# Paper Notes

## Purpose

Create or update the content of a paper note after the paper identity is already settled.

## Reads

- one paper PDF
- a stable `bibkey`
- note metadata such as `title`, `author`, `venue`, `year`, `doi`, `url`, `source`
- a provided note path
- optional existing note content

## Writes

- created or updated note content at the provided path
- optional note metadata refinements when supported by the inputs
- a status report describing whether the note is complete or intentionally partial

## Source Of Truth

- the identified paper PDF
- known metadata
- the provided note path
- the stable `bibkey`
- existing good note content when present

## Required Behavior

- stop if the note path is not given instead of guessing
- create a structured note instead of a loose text dump
- preserve good existing content unless the user asked for a rewrite
- fill missing sections before rewriting strong sections
- stay faithful to the paper and known metadata
- write a narrower partial note when extraction quality is weak instead of inventing detail

## Non-Goals

- matching the PDF to a BibTeX entry
- inventing or repairing the `bibkey`
- renaming the PDF
- deciding the archive path
- choosing the note path
- rewriting unrelated local indexes or catalogs

## Output Contract

Report at least:

- whether the note was created or updated
- whether existing metadata was reused
- whether the note is complete or intentionally partial
- which sections remain narrow because the source material was weak

## Overview

Use this skill to create or update the content of a paper note after the paper's identity is already settled.

This skill assumes the following are already known or provided:

- the target paper
- the PDF path
- the stable `bibkey`
- the note path
- any available metadata such as title, authors, venue, year, DOI, URL, or source path

Default goal: produce a complete reading note rather than a minimal resource card.

## Responsibilities

- Create a new note at a provided path from known paper metadata and PDF content.
- Update an existing note by filling missing sections or improving low-quality placeholders.
- Reuse existing frontmatter and metadata when present.
- Write a structured note body that stays faithful to the paper.
- Produce a narrower partial note when the PDF text extraction is incomplete or noisy.

Do not:

- match the PDF to a BibTeX entry
- invent or repair the `bibkey`
- rename the PDF
- choose the final archive path for the PDF
- choose the note path
- rewrite unrelated local indexes or catalogs

## Input Contract

Default inputs may include:

- one paper PDF
- a stable `bibkey`
- note metadata such as `title`, `author`, `venue`, `year`, `doi`, `url`, `source`
- a provided note path
- optional existing note content

If the note path is not given, stop and defer path selection to another workflow instead of guessing.

## Note Structure

Use a general structure that is compatible with detailed Markdown reading notes:

- frontmatter
- title
- basic information or citation
- what problem the paper solves
- core method or mechanism
- results, contributions, or main claims
- limitations, caveats, or reading reminders
- related links when enough context exists
- notes, usefulness, or takeaways

Optional extensions when the evidence supports them:

- `阅读目的`
- `后续动作`

Do not force optional sections when they would only produce filler.

## Writing Rules

- Default to a complete reading note, not a lightweight card.
- Stay faithful to the PDF and known metadata.
- Do not invent missing experiments, limitations, or implementation details.
- Prefer clear structure over ornamental wording.
- Use short, traceable quotes only when they can be located again.
- If extraction quality is poor, write a narrower but reliable note from the recoverable sections.

## Update Rules

- Preserve good existing content unless the user asked for a rewrite.
- Fill missing sections before rewriting strong sections.
- Reuse existing frontmatter fields when they are already correct.
- Add missing fields only when they can be supported by the inputs.
- Avoid churn in stable headings or metadata without a clear reason.

## Output Discipline

- If the main task is identifying which paper a PDF is or whether it duplicates an existing record, use `$paper-match`.
- If the main task is batch bibliography reconciliation or duplicate-oriented library status, use `$paper-reconcile`.
- If the main task is maintaining the missing-paper checklist, use `$paper-missing`.
- If the main task is generating or repairing the `bibkey`, use `$paper-bibkey`.
- If the main task is normalizing the PDF filename, use `$paper-rename`.
- If the main task is deciding the final archive path and moving the PDF, use `$paper-organize`.

## Commands

Prefer fast local inspection:

- Read the note: `Get-Content <note.md>`
- Read PDF metadata: `pdfinfo <file.pdf>`
- Extract the first pages: `pdftotext -f 1 -l 3 -nopgbrk -layout <file.pdf> -`
- Search local note fields: `rg -n "^title:|^source:|^bibkey:|^author:|^year:" <workspace-root>`
