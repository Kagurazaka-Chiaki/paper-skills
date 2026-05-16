---
name: paper-deep-read
description: Perform a close reading of an already-identified academic paper, turning an existing paper note or PDF into a rigorous deep-reading record with problem framing, claim/evidence analysis, method reconstruction, equations or algorithm walkthroughs, experiment audit, limitations, related knowledge links, and reusable explanations. Use when Codex needs to 精读 a paper, do close reading or deep reading, prepare a paper for research use, implementation reproduction, or skeptical technical review. This skill does not identify papers, generate bibkeys, move PDFs, or maintain indexes.
---

# Paper Deep Read

## Purpose

Append or update a rigorous `## 精读记录` section for an already-identified paper.

Use this skill after the paper identity is settled and a paper note already exists or is explicitly provided.

## Reads

- an existing paper note
- stable identifiers such as `bibkey` and optional `zotero_key`
- known paper metadata in frontmatter or the note body
- the paper PDF when available, preferably from configured external PDF roots
- the template in `references/deep-reading-template.md`

## Writes

- only the `## 精读记录` section in the target paper note by default
- a status report describing source coverage, weak evidence, and remaining review work

## Source Of Truth

- the paper PDF when available
- the existing paper note and metadata
- stable `bibkey` / `zotero_key`
- explicit user instructions about the reading goal

## Required Behavior

- preserve the existing paper note and avoid rewriting stable sections
- append `## 精读记录` when it does not exist
- update only the existing `## 精读记录` section when it already exists
- prefer configured external PDF roots when locating the PDF from a `bibkey` or title
- if the PDF is unavailable, write a partial deep-read section from the existing note and clearly mark PDF-dependent items as `未验证 / 待回看`
- scan the paper structure before writing conclusions
- distinguish claims, evidence, and caveats
- reconstruct the method in Chinese using step-by-step explanations
- use Mermaid or ASCII for pipelines when a diagram materially improves understanding
- link reusable knowledge to `03-Knowledge` and review/explanation material to `11-Review` when appropriate
- do not create additional notes unless the user explicitly asks

## Non-Goals

- identifying which paper a PDF is
- generating or repairing a `bibkey`
- renaming or moving PDFs
- deciding archive placement
- creating the initial paper note from scratch
- maintaining `papers.bib`, `papers.sqlite`, or other indexes
- turning the note into a full survey or literature review

## Workflow

1. Confirm the target paper.
   Read the existing note and identify `bibkey`, `zotero_key`, title, authors, year, and current note quality.

2. Locate the PDF when possible.
   Read `.paper-skills.json` when available and search `external_pdf_roots.paper` for a filename matching the `bibkey`, note stem, title, or short Chinese title. If no PDF root is configured or no PDF is found, continue from the note only and mark the output as partial.

3. Inspect the paper structure.
   Read or extract enough text to identify abstract, introduction, method, experiments, results, limitations, and conclusion. Do not jump directly to summary writing.

4. Build the deep-reading record.
   Use `references/deep-reading-template.md` as the default section shape. Remove headings that would only contain filler, but keep claim/evidence/caveat and implementation-risk coverage when possible.

5. Update the note.
   Insert or replace only `## 精读记录`. Preserve all other sections unless the user explicitly requested a broader rewrite.

6. Report limitations.
   Say whether the PDF was used, which parts remain `未验证 / 待回看`, and which links or follow-up actions were added.

## Reading Standards

- Treat the paper as an argument, not just a source of facts.
- Write down the paper's main question before listing contributions.
- Separate author claims from evidence that actually supports those claims.
- When explaining formulas or algorithms, state what each symbol or step is doing in the method.
- For experiments, capture what was compared, what metric was used, and what conclusion the result can or cannot support.
- For implementation-oriented reading, identify data requirements, model assumptions, hyperparameters, numerical risks, and reproduction traps.
- Do not invent missing results, ablations, limitations, or implementation details.

## Output Contract

Report at least:

- target note path and `bibkey`
- whether the PDF was found and used
- whether `## 精读记录` was appended or updated
- which sections are intentionally partial
- any suggested follow-up notes or review cards, without creating them unless requested

## Routing

- Use `paper-notes` instead when the task is to create or lightly complete an ordinary paper note.
- Use `paper-match` first when the paper identity is unknown.
- Use `paper-bibkey` first when the stable key is missing or suspect.
- Use `paper-index` only after note metadata or index records need synchronization.

## Commands

Prefer local inspection:

- Read the note with the local file-reading tool available in the current runtime.
- Search PDFs in configured external PDF roots.
- Extract PDF text when available: `pdftotext -f 1 -l 5 -nopgbrk -layout <file.pdf> -`
- Search existing knowledge links: `rg -n "<topic>|<method>|<bibkey>" <workspace-root>`
