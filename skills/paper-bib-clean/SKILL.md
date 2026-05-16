---
name: paper-bib-clean
description: Clean existing BibTeX files so they import cleanly into Zotero or other reference managers while preserving citation keys and entries. Use when Codex needs to repair malformed author lists, convert comma-separated multi-author fields to BibTeX `and` separators, prefer `Family, Given` author formatting, add Zotero-compatible local PDF attachment fields, avoid Windows drive-colon problems in BibTeX `file` fields, normalize paths to forward slashes, or validate a `.bib` file without touching PDFs or Zotero databases.
---

# Paper Bib Clean

## Purpose

Clean an existing `.bib` file for Zotero import while preserving citation keys and entries.

Use this skill when the user asks to fix, clean, repair, normalize, or make a BibTeX file importable by Zotero.

## Reads

- the target `.bib` file
- local PDF library paths when attachment fields need to be added
- optional existing PDF filenames under configured external PDF roots

## Writes

- only the target `.bib` file
- a concise summary of changed entries and validation results

## Source Of Truth

- existing citation keys in the `.bib` file
- existing entry metadata
- actual PDF filenames on disk when adding attachment fields
- explicit user path conventions

## Required Behavior

- modify only `.bib` files
- never modify PDF files
- never modify Zotero databases
- never delete entries unless the user explicitly asks
- preserve citation keys exactly, such as `@misc{hu_2026_elf,`
- convert comma-separated multi-author fields to BibTeX `and` separators
- prefer `Family, Given` author names when a safe conversion is possible
- preserve non-ASCII author names when already present
- add attachment fields only when the PDF path can be determined from user instructions or actual local files
- use forward slashes in attachment paths
- on drive-letter paths, prefer Zotero's BibTeX-importable `pdf` field:
  `pdf = {<forward-slash-absolute-or-configured-path>}`
- avoid JabRef-style `file` fields with drive-letter paths because the drive colon can be parsed as a field separator during import
- use JabRef-style `file = {Full Text:/path/to/example.pdf:application/pdf}` only when there is no Windows drive-letter colon or the target importer is known to support it
- keep unrelated fields unchanged except for necessary comma placement

## Non-Goals

- generating or changing bibkeys
- matching unknown PDFs to unknown papers
- renaming PDFs
- moving PDFs
- updating paper notes
- maintaining `papers.sqlite`
- importing into Zotero

## Workflow

1. Locate the target `.bib`.
   If the user names a `.bib`, use that file. Otherwise, read the downstream `.paper-skills.json` when available and use `external_library_bib`. If neither is available, inspect nearby bibliography files and choose the closest clear target only when unambiguous. Report the actual path used.

2. Parse entries conservatively.
   Preserve entry type, citation key, field order, and recoverable formatting. Do not drop unknown fields.

3. Fix author fields.
   For multi-author strings separated by commas, split into individual authors only when the pattern is clearly a list of people rather than one `Family, Given` name.
   Convert safe Western-style names from `Given Family` to `Family, Given`.
   Join authors with ` and `.

4. Add or update attachment fields.
   Use user-specified path rules first.
   Otherwise match PDFs by citation key prefix or existing library filenames.
   Keep paths with `/`, not `\`.
   Do not invent file paths when no plausible PDF exists.
   Prefer `pdf = {...}` for Windows paths.

5. Validate the cleaned `.bib`.
   Check that each entry still has its original citation key.
   Check that edited multi-author fields use ` and `.
   Check that each requested `pdf` or `file` path exists when local validation is possible.
   Run the bundled validation script when available.

6. Report the summary.
   Include the target file, number of entries touched, author fields repaired, attachment fields added or updated, and any entries skipped because a path or author split was ambiguous.

## Author Cleaning Rules

- Safe `Given Family` examples:
  - `Ashish Vaswani` -> `Vaswani, Ashish`
  - `Aidan N. Gomez` -> `Gomez, Aidan N.`
  - `Christopher C. Tanner` -> `Tanner, Christopher C.`
- Already-correct `Family, Given` single-author fields should be left unchanged.
- A field containing multiple `Family, Given` authors without `and` is ambiguous; repair only when the grouping is clear or the user provides the intended authors.
- Corporate authors should be preserved with braces when present.

## Validation Script

Use the bundled script after edits:

```sh
python skills/paper-bib-clean/scripts/validate_bib_for_zotero.py <target.bib>
```

The script checks:

- citation key uniqueness
- comma-separated multi-author fields that still lack `and`
- attachment paths with backslashes
- Windows drive-colon use inside `file` fields
- existence of local `pdf` paths when possible

## Commands

Prefer local checks:

- Find `.bib` files: `rg --files | rg "\\.bib$"`
- Inspect entries with the local file-reading tool available in the current runtime.
- Find PDFs by searching configured external PDF roots.
- Validate after cleanup: `python skills/paper-bib-clean/scripts/validate_bib_for_zotero.py <file.bib>`
