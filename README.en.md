# paper-skills

`paper-skills` is a generic source repository for reusable paper-management skills.

It is intentionally organized as a public `skills/` tree instead of a vendor-specific hidden directory such as `.agents/skills/` or `.codex/skills/`. The repository is meant to be copied, vendored, or installed into different agent runtimes without rewriting the core skill content.

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
    paper-rename/
    paper-organize/
    paper-ingest/
    paper-notes/
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
- `paper-rename`: normalize the PDF filename from a confirmed bibkey
- `paper-organize`: place a paper into its final archive location
- `paper-ingest`: orchestrate the end-to-end ingest pipeline
- `paper-notes`: create or update structured paper notes
- `paper-missing`: maintain missing-paper checklists
- `paper-reconcile`: reconcile library-wide coverage and duplicate state
- `paper-index`: maintain lightweight `papers.bib` and `papers.sqlite` indexes

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
