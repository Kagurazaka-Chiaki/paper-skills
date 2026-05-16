---
name: paper-skills
description: Dispatch paper-management requests to the canonical internal skills in `skills/*/SKILL.md`, choosing the smallest correct subskill or subskill sequence without depending on external bridge directories.
---

# Paper Skills

## Purpose

Use this skill as the single entrypoint for the `paper-skills` repository when the runtime can discover this root `SKILL.md` but does not directly register the nested skills under `skills/*/SKILL.md`.

This file is a dispatcher. The source of truth remains the internal child skills in this repository.

## Canonical Child Skills

Only dispatch to these internal files:

- `skills/paper-match/SKILL.md`
- `skills/paper-bibkey/SKILL.md`
- `skills/paper-bib-clean/SKILL.md`
- `skills/paper-rename/SKILL.md`
- `skills/paper-organize/SKILL.md`
- `skills/paper-ingest/SKILL.md`
- `skills/paper-notes/SKILL.md`
- `skills/paper-deep-read/SKILL.md`
- `skills/paper-missing/SKILL.md`
- `skills/paper-reconcile/SKILL.md`
- `skills/paper-index/SKILL.md`

Do not rely on external bridge paths such as:

- `.codex/skills/paper-match/SKILL.md`
- `.codex/skills/paper-bibkey/SKILL.md`
- other vendor-specific duplicated entrypoints outside this repository

## Dispatch Rules

1. Determine the smallest correct child skill for the task.
2. Read only the needed child `SKILL.md` file under `skills/`.
3. Follow that child skill as the operational source of truth.
4. If the task spans multiple stages, sequence the child skills explicitly and keep each stage dependent on the previous stage's stable output.
5. If the user asks for a generic end-to-end paper workflow, default first to `skills/paper-ingest/SKILL.md`.

## Routing Guide

Use:

- `skills/paper-match/SKILL.md` for paper identity resolution or duplicate detection
- `skills/paper-bibkey/SKILL.md` for generating or repairing a bibkey
- `skills/paper-bib-clean/SKILL.md` for cleaning existing BibTeX files for Zotero import without changing citation keys, PDFs, or Zotero databases
- `skills/paper-rename/SKILL.md` for PDF filename normalization
- `skills/paper-organize/SKILL.md` for archive placement and reference sync
- `skills/paper-ingest/SKILL.md` for orchestration across multiple stages
- `skills/paper-notes/SKILL.md` for writing or updating a paper note
- `skills/paper-deep-read/SKILL.md` for close-reading an identified paper and appending or updating `## 精读记录`
- `skills/paper-missing/SKILL.md` for missing-paper checklist maintenance
- `skills/paper-reconcile/SKILL.md` for collection-level bibliography reconciliation
- `skills/paper-index/SKILL.md` for maintaining repository-local minimal `.bib` files, `papers.sqlite`, and `resources.sqlite`

Route requests for `精读`, close reading, deep reading, research-use reading, reproduction-oriented understanding, or skeptical technical review to `skills/paper-deep-read/SKILL.md`. Keep ordinary note creation or lightweight note completion routed to `skills/paper-notes/SKILL.md`.

Route requests to clean `.bib` files, repair malformed author fields, convert comma-separated author lists to `and`, add Zotero `file` fields, or make BibTeX import cleanly into Zotero to `skills/paper-bib-clean/SKILL.md`. Do not route these cleanup-only requests to `paper-bibkey` unless the user wants keys generated or changed.

## Required Behavior

- Prefer one child skill when one is sufficient.
- Use multiple child skills only when the task genuinely spans multiple stages.
- Keep all relative references inside this repository rooted to the selected child skill directory.
- When a selected child skill references `scripts/`, `templates/`, or `references/`, resolve those paths relative to that child skill's own directory.
- If two child skills might apply, choose the earlier dependency in the pipeline instead of skipping ahead.

## Non-Goals

- redefining the behavior of the child skills
- duplicating the full contents of the child `SKILL.md` files here
- depending on hidden runtime-specific mirror directories as the source of truth

## Output Discipline

- Report which child skill or child-skill sequence was selected.
- Keep the dispatch explanation short.
- If a task is ambiguous, stop at the earliest unresolved dependency and route to the correct child skill instead of guessing.
