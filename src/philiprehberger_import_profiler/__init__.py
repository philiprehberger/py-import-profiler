"""Show how long each Python import takes during startup."""

from __future__ import annotations

import builtins
import time
from dataclasses import dataclass, field
from typing import Any


__all__ = [
    "profile_imports",
    "ImportReport",
    "ImportEntry",
]


@dataclass
class ImportEntry:
    """Timing data for a single import."""

    name: str
    duration_ms: float
    children: list[ImportEntry] = field(default_factory=list)
    parent: str = ""

    @property
    def self_ms(self) -> float:
        """Duration minus children's duration."""
        child_total = sum(c.duration_ms for c in self.children)
        return max(0.0, self.duration_ms - child_total)


@dataclass
class ImportReport:
    """Profiling results for all imports."""

    entries: list[ImportEntry] = field(default_factory=list)
    _by_name: dict[str, ImportEntry] = field(default_factory=dict, repr=False)

    @property
    def total_ms(self) -> float:
        return sum(e.duration_ms for e in self.entries if not e.parent)

    @property
    def module_count(self) -> int:
        return len(self.entries)

    def slowest(self, n: int = 10) -> list[ImportEntry]:
        """Return the *n* slowest imports by total duration.

        Args:
            n: Number of entries to return.

        Returns:
            List sorted by duration descending.
        """
        return sorted(self.entries, key=lambda e: e.duration_ms, reverse=True)[:n]

    def filter(self, prefix: str) -> ImportReport:
        """Return a new ImportReport containing only entries whose name starts with *prefix*.

        Args:
            prefix: Module name prefix to match.

        Returns:
            New ImportReport with the filtered entries. The original report is not mutated.
        """
        filtered = [e for e in self.entries if e.name.startswith(prefix)]
        return ImportReport(
            entries=filtered,
            _by_name={e.name: e for e in filtered},
        )

    def print_tree(self, *, threshold_ms: float = 0.0) -> None:
        """Print an indented tree of import times.

        Args:
            threshold_ms: Hide imports faster than this.
        """
        roots = [e for e in self.entries if not e.parent]
        for root in sorted(roots, key=lambda e: e.duration_ms, reverse=True):
            _print_entry(root, "", True, threshold_ms)

    def to_dict(self) -> list[dict[str, Any]]:
        """Export entries as a list of dicts."""
        return [
            {
                "name": e.name,
                "duration_ms": round(e.duration_ms, 2),
                "self_ms": round(e.self_ms, 2),
                "parent": e.parent,
            }
            for e in self.entries
        ]


def profile_imports(module_name: str) -> ImportReport:
    """Profile all imports triggered by importing *module_name*.

    Temporarily patches ``builtins.__import__`` to measure timing,
    then restores the original.

    Args:
        module_name: The top-level module to import.

    Returns:
        ImportReport with timing data for all imports.
    """
    report = ImportReport()
    original_import = builtins.__import__
    import_stack: list[str] = []

    def profiled_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name in report._by_name:
            return original_import(name, *args, **kwargs)

        parent = import_stack[-1] if import_stack else ""
        import_stack.append(name)

        start = time.perf_counter()
        try:
            result = original_import(name, *args, **kwargs)
        finally:
            elapsed = (time.perf_counter() - start) * 1000
            import_stack.pop()

        entry = ImportEntry(name=name, duration_ms=elapsed, parent=parent)
        report.entries.append(entry)
        report._by_name[name] = entry

        if parent and parent in report._by_name:
            report._by_name[parent].children.append(entry)

        return result

    builtins.__import__ = profiled_import
    try:
        __import__(module_name)
    finally:
        builtins.__import__ = original_import

    return report


def _print_entry(entry: ImportEntry, prefix: str, is_last: bool, threshold_ms: float) -> None:
    if entry.duration_ms < threshold_ms:
        return

    connector = "\u2514\u2500\u2500 " if is_last else "\u251c\u2500\u2500 "
    print(f"{prefix}{connector}{entry.name} ({entry.duration_ms:.1f}ms)")

    child_prefix = prefix + ("    " if is_last else "\u2502   ")
    visible_children = [c for c in entry.children if c.duration_ms >= threshold_ms]
    for i, child in enumerate(visible_children):
        _print_entry(child, child_prefix, i == len(visible_children) - 1, threshold_ms)
