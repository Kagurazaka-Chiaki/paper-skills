---
name: paper-ingest
description: Ingest a paper into a local library end-to-end by inspecting the current state, determining which paper-management steps are still missing, and routing the work through the appropriate paper skills. Use when Codex needs a single capability entry for handling an incoming paper PDF or metadata record from initial identification through bibkey, filename normalization, archive placement, note creation, or collection-level reconciliation.
---

# Paper Ingest

## Purpose

Act as the orchestration entrypoint for end-to-end paper-management work and route the task to the earliest missing ingestion stage.

## Reads

- incoming PDFs or paper records
- existing bibliography files
- local notes, records, indexes, and archive layout
- current outputs of the other paper skills when they already exist

## Writes

- no mandatory direct writes
- optional staged plan or ingest status summary for the downstream workflow
- downstream repository writes only through the delegated specialized skills

## Source Of Truth

- current local paper state
- the earliest unresolved dependency in the ingest pipeline
- outputs from specialized paper skills once they exist
- the requested ingest goal

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
- re-check progress after each completed stage
- stop once the requested ingest goal is satisfied

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
- the stop condition for the requested ingest goal

## Overview

Use this skill as the high-level entry point for paper-management work.

This skill does not replace the specialized paper skills. It decides which of them are needed, in what order, and which steps can be skipped because the current state is already good enough.

Typical downstream skills:

- `$paper-match`
- `$paper-bibkey`
- `$paper-rename`
- `$paper-organize`
- `$paper-notes`
- `$paper-missing`
- `$paper-reconcile`

## Responsibilities

- Inspect the current state of an incoming paper in the local workspace.
- Decide which ingestion steps are already complete and which are still missing.
- Route the task through the appropriate specialized paper skills.
- Keep the execution order coherent so later steps consume stable outputs from earlier steps.
- Prefer the smallest necessary ingestion path instead of blindly redoing every step.

Do not:

- duplicate the detailed logic that already belongs to a specialized paper skill
- invent a parallel workflow that bypasses the existing paper-skill split
- force all steps to run when the paper is already partially ingested

## State Model

Think in terms of ingestion stages:

1. Identity known?
   If not, use `$paper-match`.

2. Stable bibkey available?
   If not, use `$paper-bibkey`.

3. Filename normalized?
   If not, use `$paper-rename`.

4. Archived into final library location?
   If not, use `$paper-organize`.

5. Note body created or updated?
   If needed, use `$paper-notes`.

6. Missing-paper checklist updated?
   If needed, use `$paper-missing`.

7. Collection-level bibliography status updated?
   If needed for broader batch reconciliation or duplicate tracking, use `$paper-reconcile`.

## Workflow

1. Inspect the current inputs and local state.
   Determine whether the target is a raw PDF, an already-matched paper, an already-keyed paper, a misplaced archive item, an unwritten note, or a collection-level reconciliation task.

2. Choose the earliest missing stage.
   Start from the earliest unresolved dependency rather than jumping straight to later steps.

3. Route to the correct specialized skill.
   Use:
   - `$paper-match` for per-paper identity resolution and duplicate detection
   - `$paper-bibkey` for bibkey generation or repair
   - `$paper-rename` for stable filename normalization
   - `$paper-organize` for final archive placement and reference updates
   - `$paper-notes` for note-body creation or enrichment
   - `$paper-missing` for missing-paper checklist maintenance
   - `$paper-reconcile` for library-wide BibTeX reconciliation and duplicate-oriented status maintenance

4. Re-check after each stage.
   Confirm that the output of one stage is sufficient input for the next stage before continuing.

5. Stop once the requested ingestion goal is satisfied.
   Do not continue into optional downstream work unless the user asked for full ingestion or the later stage is a clear dependency.

## Routing Rules

- If the user asks “ingest this paper” without specifying sub-steps, treat that as an end-to-end orchestration request and start here.
- If the paper identity is uncertain, never skip directly to bibkey, rename, organize, or note-writing.
- If the bibkey is unstable, do not organize or finalize the note around it first.
- If the filename is already stable and acceptable, do not rename it just for neatness.
- If the workspace keeps paper notes coupled to attachment basenames, treat note-file renaming as part of the filename-normalization stage rather than as a separate note-writing stage.
- If the archive location is already correct, do not move it again.
- If the note already exists and is strong, update it only when the user asked for enrichment.

## Output Discipline

- Report the current ingestion stage clearly.
- Explain which specialized skill is the next correct step and why.
- Prefer incremental progress over full reprocessing.
- Keep collection-level reconciliation separate from single-paper ingestion unless the user asked for both.

## Commands

Prefer fast local inspection:

- Search local paper metadata: `rg -n "^bibkey:|^source:|^doi:|^year:" <workspace-root>`
- Search bibliography entries: `rg -n "^@(article|inproceedings|misc)\\{" <bibfile>`
- List candidate PDFs: `rg --files <workspace-root> | rg "\\.pdf$"`
- Search existing references: `rg -n "\\.pdf|source:|bibkey:" <workspace-root>`
