# AGENTS.md

## Purpose

This repository is a portable source repository for paper-management skills.

The published source of truth is the visible `skills/` tree. Optional vendor metadata may exist under `adapters/`, but it must not redefine the core skill content.

## Rules

- Publish skills under `skills/`, not under vendor-specific hidden directories.
- Keep the repository vendor-neutral and file-based.
- Keep skill names lowercase and hyphenated.
- Keep canonical bibkeys ASCII-only.
- Keep resource references relative to the skill directory.
- Do not add placeholder files with no operational value.
- Keep the main GitHub-facing `README.md` in Chinese by default; use `README.en.md` for the English version.
- Keep repository docs under `docs/` in Chinese by default unless a specific bilingual split is needed.

## Skill Expectations

Each skill should explicitly define:

- purpose
- reads
- writes
- source of truth
- required behavior
- non-goals
- output contract

Keep skills single-purpose and composable.

Optional support directories are:

- `templates/`
- `scripts/`
- `references/`

Create them only when they contain real content.

## Portability

- Treat `skills/` as the canonical source layout.
- Do not make `.agents/`, `.codex/`, or other hidden vendor paths the primary published structure.
- Keep vendor-specific metadata outside the main skill folders.
- Use `adapters/openai/<skill-name>/openai.yaml` for OpenAI-specific compatibility metadata.
- Prefer plain Markdown and small helper resources over framework-heavy packaging.
- When conventions change, update the affected skill and the relevant docs together.

## Repository References

Use these files as the main repository-level references:

- `README.md`
- `README.en.md`
- `docs/conventions.md`
- `docs/portability.md`

If repository-level instructions conflict, prefer:

1. explicit user request
2. `AGENTS.md`
3. `docs/conventions.md`
4. `docs/portability.md`

## Change Discipline

When changing repository structure or conventions:

1. update the affected `skills/<name>/SKILL.md`
2. update any affected `adapters/openai/<name>/openai.yaml`
3. update `README.md` / `README.en.md` if the public structure changed
4. keep `docs/conventions.md` and `docs/portability.md` aligned

Optimize for long-term portability over tool-specific convenience.
