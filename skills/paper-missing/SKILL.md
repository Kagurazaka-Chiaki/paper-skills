---
name: paper-missing
description: Maintain missing-paper checklists by comparing expected bibliography entries against current local coverage, removing newly covered items, and keeping the missing summary accurate without redoing per-paper identity work from scratch.
---

# Paper Missing

## Purpose

Maintain the still-missing view of a paper collection.

## Reads

- one or more bibliography files
- an existing missing-paper checklist
- local PDFs, notes, records, or indexes
- optional precomputed match results

## Writes

- updated missing-paper checklist
- updated missing counts or newly-covered summaries when the local format supports them

## Source Of Truth

- expected bibliography coverage
- reliable local evidence that a paper is already present
- confirmed match results when they exist

## Required Behavior

- compare the expected paper set against current local coverage
- remove newly covered papers conservatively
- keep unresolved or ambiguous cases in the missing set
- preserve user-maintained annotations unless they are clearly obsolete

## Non-Goals

- per-paper identity matching as the main task
- bibkey generation or repair
- filename normalization
- archive placement
- note writing

## Output Contract

Report at least:

- entries still missing
- entries newly covered
- whether the checklist changed
- the updated missing count
