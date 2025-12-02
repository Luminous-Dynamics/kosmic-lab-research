#!/usr/bin/env python3
"""
Lightweight magic-number checker for Python files.

Prints warnings for numeric literals that are inlined rather than referenced
via a named constant. This hook is intentionally advisory (exit code 0) to
avoid blocking commits; it nudges contributors toward clearer code.

Skip a specific line by adding a trailing comment containing one of:
  - MAGIC_OK
  - NOQA:MAGIC

Numbers considered benign (ignored): -1, 0, 1, 2 and their float forms.
Assignments to ALL_CAPS names are treated as constant definitions and allowed.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Iterable, List, Tuple

ALLOWED_VALUES = {-1, 0, 1, 2, -1.0, 0.0, 1.0, 2.0}
SKIP_MARKERS = ("MAGIC_OK", "NOQA:MAGIC")


class MagicNumberVisitor(ast.NodeVisitor):
    def __init__(self, source_lines: List[str]) -> None:
        self.source_lines = source_lines
        self.warnings: List[Tuple[int, str]] = []

    def visit_Assign(self, node: ast.Assign) -> None:  # type: ignore[override]
        # If assigning to ALL_CAPS, treat as defining a constant (allowed)
        targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
        is_constant_def = any(name.isupper() for name in targets)
        if is_constant_def:
            return
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:  # type: ignore[override]
        if not isinstance(node.value, (int, float)):
            return
        if node.value in ALLOWED_VALUES:
            return
        # Skip if line is explicitly marked ok
        try:
            line = self.source_lines[node.lineno - 1]
        except IndexError:
            line = ""
        if any(marker in line for marker in SKIP_MARKERS):
            return
        # Skip if part of a type annotation or simple range
        parent = getattr(node, "parent", None)
        if isinstance(parent, (ast.AnnAssign,)):
            return
        self.warnings.append((node.lineno, f"Magic number {node.value!r} detected"))


def attach_parents(node: ast.AST) -> None:
    for child in ast.iter_child_nodes(node):
        child.parent = node  # type: ignore[attr-defined]
        attach_parents(child)


def check_file(path: Path) -> List[Tuple[int, str]]:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    attach_parents(tree)
    visitor = MagicNumberVisitor(text.splitlines())
    visitor.visit(tree)
    return visitor.warnings


def main(argv: Iterable[str]) -> int:
    paths = [Path(p) for p in argv if p.endswith(".py")]
    total = 0
    for path in paths:
        warnings = check_file(path)
        for lineno, msg in warnings:
            print(f"{path}:{lineno}: {msg}")
        total += len(warnings)
    # Advisory only: do not fail the commit
    if total:
        print(f"\n⚠️  Found {total} potential magic number(s). Consider using named constants.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

