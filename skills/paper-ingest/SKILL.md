---
name: paper-ingest
description: Route an incoming paper through the paper-management pipeline by inspecting current state, determining which steps are missing, and handing work off to the correct skills from matching through rename, organize, note-writing, missing-paper maintenance, or collection reconciliation.
---

# Paper Ingest

## Purpose

Act as the orchestration entrypoint for end-to-end paper-management work.

## Reads

- incoming PDFs or paper records
- existing bibliography files
- local notes, records, indexes, and archive layout
- current outputs of the other paper skills when they already exist

## Writes

- no mandatory direct writes
- optional staged plan or ingest status summary for the downstream workflow

## Source Of Truth

- current local paper state
- the earliest unresolved dependency in the ingest pipeline
- outputs from specialized paper skills once they exist

## Required Behavior

- inspect the current ingest stage before doing work
- start from the earliest unresolved dependency
- route identity work to `paper-match`
- route bibkey work to `paper-bibkey`
- route filename work to `paper-rename`
- route archive placement to `paper-organize`
- route note creation or enrichment to `paper-notes`
- route missing checklist work to `paper-missing`
- route collection-level coverage work to `paper-reconcile`

## Non-Goals

- duplicating the detailed logic that belongs to specialized skills
- forcing every ingest step to run when later stages are already valid
- replacing the specialized skill split with a monolithic workflow

## Output Contract

Report at least:

- current ingest stage
- the next required skill
- why that step is next
- which later stages can be skipped or deferred
