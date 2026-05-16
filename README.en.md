# paper-skills

`paper-skills` is a generic source repository for reusable paper-management skills.

It is intentionally organized as a public `skills/` tree instead of a vendor-specific hidden directory such as `.agents/skills/` or `.codex/skills/`. The repository is meant to be copied, vendored, or installed into different agent runtimes without rewriting the core skill content.

Paths and library layouts belong to downstream projects. Provide a `.paper-skills.json` file at the downstream workspace root, or pass explicit script arguments. This source repository must not assume a specific vault layout, drive letter, or operating-system shell.

## Layout

```text
paper-skills/
  README.md
  README.en.md
  README.zh.md
  AGENTS.md
  skills/
    paper-match/
    paper-bibkey/
    paper-bib-clean/
    paper-rename/
    paper-organize/
    paper-ingest/
    paper-notes/
    paper-deep-read/
    paper-missing/
    paper-reconcile/
    paper-index/
  docs/
    conventions.md
    portability.md
  adapters/
    openai/
```

## Included skills

- `paper-match`: identify what a PDF actually is and report confidence or ambiguity
- `paper-bibkey`: generate or repair a stable bibkey
- `paper-bib-clean`: clean existing BibTeX files so they import cleanly into Zotero
- `paper-rename`: normalize the PDF filename from a confirmed bibkey
- `paper-organize`: place a paper into its final archive location
- `paper-ingest`: orchestrate the end-to-end ingest pipeline
- `paper-notes`: create or update structured paper notes
- `paper-deep-read`: close-read an identified paper and append a rigorous deep-reading section
- `paper-missing`: maintain missing-paper checklists
- `paper-reconcile`: reconcile library-wide coverage and duplicate state
- `paper-index`: maintain repository-local minimal `.bib`, `papers.sqlite`, and `resources.sqlite` indexes

## Downstream Configuration

Downstream projects can describe their own resource layout with `.paper-skills.json`:

```json
{
  "resource_root": "<resource-root>",
  "paper_notes_dir": "<paper-note-dir>",
  "resource_bibs": {
    "paper": "<papers.bib>",
    "book": "<books.bib>",
    "reference-note": "<reference-notes.bib>"
  },
  "paper_sqlite": "<papers.sqlite>",
  "resource_sqlite": "<resources.sqlite>",
  "external_library_bib": "<external-library.bib>",
  "external_pdf_roots": {
    "paper": "<paper-pdf-root>",
    "book": "<book-pdf-root>",
    "reference-note": "<reference-note-pdf-root>"
  }
}
```

Without config, scripts may only use uniquely discoverable filenames such as `papers.bib`, `books.bib`, `reference-notes.bib`, `papers.sqlite`, and `resources.sqlite`. If multiple candidates exist, require explicit config or CLI paths.

## Principles

- portable, non-hidden repository layout
- ASCII canonical identifiers
- Chinese allowed in display text, not in bibkeys
- single-purpose skills instead of one monolithic workflow
- plain Markdown and small helper resources over packaging-heavy solutions
- `skills/` is the published source of truth
- `adapters/openai/` is optional compatibility metadata, not the main skill layout

## Docs

- [`docs/conventions.md`](docs/conventions.md)
- [`docs/portability.md`](docs/portability.md)
