from __future__ import annotations

import argparse
from pathlib import Path

from paper_index_sync.app import SyncIndexApp
from paper_index_sync.config import apply_cli_overrides, load_index_config
from paper_index_sync.models import SyncOptions


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-root", required=True)
    parser.add_argument("--config", type=Path, help="Path to a downstream .paper-skills.json config.")
    parser.add_argument("--paper-notes-dir")
    parser.add_argument("--paper-bib")
    parser.add_argument("--book-bib")
    parser.add_argument("--reference-note-bib")
    parser.add_argument("--paper-sqlite")
    parser.add_argument("--resource-sqlite")
    parser.add_argument("--external-library-bib")
    parser.add_argument(
        "--strict-basename",
        action="store_true",
        help="Return a non-zero status when note/pdf basenames do not match.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned sync without writing BibTeX or SQLite files.",
    )
    parser.add_argument(
        "--prune-stale",
        action="store_true",
        help="Delete SQLite rows that are not present in the current input set.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    workspace_root = Path(args.workspace_root).resolve()
    config = load_index_config(workspace_root, args.config)
    config = apply_cli_overrides(
        config,
        workspace_root,
        paper_notes_dir=args.paper_notes_dir,
        paper_bib=args.paper_bib,
        book_bib=args.book_bib,
        reference_note_bib=args.reference_note_bib,
        paper_sqlite=args.paper_sqlite,
        resource_sqlite=args.resource_sqlite,
        external_library_bib=args.external_library_bib,
    )
    options = SyncOptions(
        dry_run=args.dry_run,
        prune_stale=args.prune_stale,
        strict_basename=args.strict_basename,
    )
    return SyncIndexApp(workspace_root, config, options).run()


if __name__ == "__main__":
    raise SystemExit(main())
