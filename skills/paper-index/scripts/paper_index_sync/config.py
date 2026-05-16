from __future__ import annotations

import json
from pathlib import Path

from .models import DISCOVERABLE_BIBS, RESOURCE_KINDS, SKIP_DIRS, IndexConfig


def workspace_display_path(path: Path, workspace_root: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(workspace_root)).replace("\\", "/")
    except ValueError:
        return str(resolved).replace("\\", "/")


def resolve_config_path(workspace_root: Path, value: object) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = workspace_root / path
    return path.resolve()


def iter_named_files(workspace_root: Path, filename: str) -> list[Path]:
    matches: list[Path] = []
    for path in workspace_root.rglob(filename):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file():
            matches.append(path.resolve())
    return sorted(matches)


def unique_discovered_file(workspace_root: Path, filename: str) -> Path | None:
    matches = iter_named_files(workspace_root, filename)
    if len(matches) > 1:
        rendered = "\n".join(f"- {workspace_display_path(path, workspace_root)}" for path in matches)
        raise SystemExit(
            f"Multiple {filename} candidates found. Pass --config or an explicit path.\n{rendered}"
        )
    return matches[0] if matches else None


def common_parent(paths: list[Path]) -> Path | None:
    if not paths:
        return None
    common = Path(paths[0]).resolve()
    if common.is_file():
        common = common.parent
    for path in paths[1:]:
        candidate = Path(path).resolve()
        if candidate.is_file():
            candidate = candidate.parent
        while common != common.parent and common not in (candidate, *candidate.parents):
            common = common.parent
    return common


def config_from_json(workspace_root: Path, config_path: Path) -> IndexConfig:
    data = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"Config must be a JSON object: {config_path}")

    resource_bibs: dict[str, Path] = {}
    raw_bibs = data.get("resource_bibs", {})
    if isinstance(raw_bibs, dict):
        for kind in RESOURCE_KINDS:
            path = resolve_config_path(workspace_root, raw_bibs.get(kind))
            if path is not None:
                resource_bibs[kind] = path

    return IndexConfig(
        paper_notes_dir=resolve_config_path(workspace_root, data.get("paper_notes_dir")),
        resource_bibs=resource_bibs,
        paper_sqlite=resolve_config_path(workspace_root, data.get("paper_sqlite")),
        resource_sqlite=resolve_config_path(workspace_root, data.get("resource_sqlite")),
        external_library_bib=resolve_config_path(workspace_root, data.get("external_library_bib")),
    )


def discover_config(workspace_root: Path) -> IndexConfig:
    resource_bibs: dict[str, Path] = {}
    for kind, filename in DISCOVERABLE_BIBS.items():
        path = unique_discovered_file(workspace_root, filename)
        if path is not None:
            resource_bibs[kind] = path

    paper_bib = resource_bibs.get("paper")
    paper_notes_dir = paper_bib.parent if paper_bib is not None else None

    discovered_paper_sqlite = unique_discovered_file(workspace_root, "papers.sqlite")
    if discovered_paper_sqlite is None and paper_bib is not None:
        discovered_paper_sqlite = paper_bib.parent / "papers.sqlite"

    discovered_resource_sqlite = unique_discovered_file(workspace_root, "resources.sqlite")
    if discovered_resource_sqlite is None:
        parent = common_parent(list(resource_bibs.values()))
        if parent is not None:
            discovered_resource_sqlite = parent / "resources.sqlite"

    return IndexConfig(
        paper_notes_dir=paper_notes_dir,
        resource_bibs=resource_bibs,
        paper_sqlite=discovered_paper_sqlite,
        resource_sqlite=discovered_resource_sqlite,
    )


def load_index_config(workspace_root: Path, config_path: Path | None) -> IndexConfig:
    if config_path is not None:
        return config_from_json(workspace_root, config_path.resolve())
    default_config = workspace_root / ".paper-skills.json"
    if default_config.exists():
        return config_from_json(workspace_root, default_config)
    return discover_config(workspace_root)


def apply_cli_overrides(
    config: IndexConfig,
    workspace_root: Path,
    *,
    paper_notes_dir: str | None = None,
    paper_bib: str | None = None,
    book_bib: str | None = None,
    reference_note_bib: str | None = None,
    paper_sqlite: str | None = None,
    resource_sqlite: str | None = None,
    external_library_bib: str | None = None,
) -> IndexConfig:
    if paper_notes_dir:
        config.paper_notes_dir = resolve_config_path(workspace_root, paper_notes_dir)
    overrides = (
        ("paper", paper_bib),
        ("book", book_bib),
        ("reference-note", reference_note_bib),
    )
    for kind, value in overrides:
        path = resolve_config_path(workspace_root, value)
        if path is not None:
            config.resource_bibs[kind] = path
    if paper_sqlite:
        config.paper_sqlite = resolve_config_path(workspace_root, paper_sqlite)
    if resource_sqlite:
        config.resource_sqlite = resolve_config_path(workspace_root, resource_sqlite)
    if external_library_bib:
        config.external_library_bib = resolve_config_path(workspace_root, external_library_bib)
    return config
