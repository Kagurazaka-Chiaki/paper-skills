from __future__ import annotations

import sys
from pathlib import Path

from .bibtex import (
    load_resource_records,
    plan_external_library_keywords_merge,
    plan_paper_bib_merge,
    write_external_library_keywords,
    write_paper_bib,
)
from .config import workspace_display_path
from .models import RESOURCE_KINDS, IndexConfig, PaperRecord, ResourceRecord, SyncOptions
from .notes import load_paper_records
from .sqlite_store import plan_sqlite_sync, write_paper_sqlite, write_resource_sqlite


class SyncIndexApp:
    def __init__(self, workspace_root: Path, config: IndexConfig, options: SyncOptions) -> None:
        self.workspace_root = workspace_root.resolve()
        self.config = config
        self.options = options

    def run(self) -> int:
        has_paper_notes = self.config.paper_notes_dir is not None and self.config.paper_notes_dir.exists()
        paper_records = load_paper_records(self.workspace_root, self.config.paper_notes_dir)

        self._print_config_summary()
        print(f"Paper note records: {len(paper_records)}")

        if has_paper_notes and self.config.paper_sqlite is not None:
            self._sync_paper_sqlite(paper_records)

        if has_paper_notes and "paper" in self.config.resource_bibs:
            self._sync_paper_bib(paper_records)

        resource_records = load_resource_records(
            self.workspace_root,
            paper_records,
            self.config.resource_bibs,
        )
        if self.config.resource_sqlite is not None:
            self._sync_resource_sqlite(resource_records)

        if self.config.external_library_bib is not None:
            self._sync_external_library_keywords(resource_records)

        print(f"Synced {len(paper_records)} paper records")
        print(f"Synced {len(resource_records)} resource records")

        mismatches = collect_basename_mismatches(paper_records)
        if mismatches:
            print("Basename mismatches detected:", file=sys.stderr)
            for mismatch in mismatches:
                print(f"- {mismatch}", file=sys.stderr)
            if self.options.strict_basename:
                return 2
        return 0

    def _sync_paper_bib(self, paper_records: list[PaperRecord]) -> None:
        paper_bib = self.config.resource_bibs["paper"]
        merge_plan = plan_paper_bib_merge(paper_bib, paper_records)
        print(
            "Paper bib merge: "
            f"preserved={merge_plan.summary.preserved}, "
            f"updated={merge_plan.summary.updated}, "
            f"added={merge_plan.summary.added}"
        )
        if not self.options.dry_run:
            write_paper_bib(paper_bib, paper_records)

    def _sync_paper_sqlite(self, paper_records: list[PaperRecord]) -> None:
        assert self.config.paper_sqlite is not None
        incoming_keys = {record.bibkey for record in paper_records}
        plan = plan_sqlite_sync(self.config.paper_sqlite, "papers", "bibkey", incoming_keys)
        print(
            "Paper sqlite: "
            f"incoming={plan.summary.incoming}, "
            f"existing={plan.summary.existing}, "
            f"stale={plan.summary.stale}, "
            f"prune_stale={self.options.prune_stale}"
        )
        if not self.options.dry_run:
            write_paper_sqlite(
                self.config.paper_sqlite,
                paper_records,
                prune_stale=self.options.prune_stale,
            )

    def _sync_resource_sqlite(self, resource_records: list[ResourceRecord]) -> None:
        assert self.config.resource_sqlite is not None
        resource_records_keys = {record.key for record in resource_records}
        plan = plan_sqlite_sync(self.config.resource_sqlite, "resources", "key", resource_records_keys)
        print(
            "Resource sqlite: "
            f"incoming={plan.summary.incoming}, "
            f"existing={plan.summary.existing}, "
            f"stale={plan.summary.stale}, "
            f"prune_stale={self.options.prune_stale}"
        )
        if len(resource_records) != len(resource_records_keys):
            print(
                f"Warning: {len(resource_records) - len(resource_records_keys)} duplicate resource keys detected",
                file=sys.stderr,
            )
        if not self.options.dry_run:
            write_resource_sqlite(
                self.config.resource_sqlite,
                resource_records,
                prune_stale=self.options.prune_stale,
            )

    def _sync_external_library_keywords(self, resource_records: list[ResourceRecord]) -> None:
        assert self.config.external_library_bib is not None
        plan = plan_external_library_keywords_merge(self.config.external_library_bib, resource_records)
        print(
            "External library keywords: "
            f"matched={plan.matched}, "
            f"changed={plan.changed}, "
            f"unchanged={plan.unchanged}, "
            f"missing={plan.missing}"
        )
        if not self.options.dry_run:
            write_external_library_keywords(self.config.external_library_bib, resource_records)

    def _print_config_summary(self) -> None:
        def show(path: Path | None) -> str:
            return workspace_display_path(path, self.workspace_root) if path is not None else "<none>"

        print("Index targets:")
        print(f"- paper notes: {show(self.config.paper_notes_dir)}")
        for kind in RESOURCE_KINDS:
            print(f"- {kind} bib: {show(self.config.resource_bibs.get(kind))}")
        print(f"- paper sqlite: {show(self.config.paper_sqlite)}")
        print(f"- resource sqlite: {show(self.config.resource_sqlite)}")
        print(f"- external library bib: {show(self.config.external_library_bib)}")
        print(f"- dry run: {self.options.dry_run}")
        print(f"- prune stale: {self.options.prune_stale}")


def stem_for_rel_path(path_str: str) -> str:
    if not path_str:
        return ""
    return Path(path_str.replace("\\", "/")).stem


def collect_basename_mismatches(records: list[PaperRecord]) -> list[str]:
    mismatches: list[str] = []
    for record in records:
        note_stem = stem_for_rel_path(record.note_path)
        pdf_stem = stem_for_rel_path(record.pdf_path)
        if not note_stem or not pdf_stem:
            continue
        if note_stem != pdf_stem:
            mismatches.append(
                f"{record.bibkey}: note='{record.note_path}' pdf='{record.pdf_path}'"
            )
    return mismatches
