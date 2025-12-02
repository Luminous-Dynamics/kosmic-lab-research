"""Nox sessions for Kosmic Lab.

These sessions proxy to Poetry-managed tools to avoid duplicating dependency
management. Ensure you ran `poetry install` first.
"""
from __future__ import annotations

import nox


@nox.session
def tests(session: nox.Session) -> None:
    """Run pytest (fast path). Pass extra args with `-p` or `--`.

    Example: poetry run nox -s tests -- -k historical
    """
    session.run("poetry", "run", "pytest", "-q", *session.posargs, external=True)


@nox.session
def lint(session: nox.Session) -> None:
    """Run pre-commit hooks across the repo."""
    session.run("poetry", "run", "pre-commit", "run", "--all-files", external=True)


@nox.session
def type(session: nox.Session) -> None:
    """Run mypy type checking (strict, with ignores for missing imports)."""
    session.run("poetry", "run", "mypy", "--strict", "--ignore-missing-imports", ".", external=True)


@nox.session
def format_check(session: nox.Session) -> None:
    """Check code formatting and basic lint (black --check + ruff)."""
    session.run("poetry", "run", "black", "--check", "core", "fre", "historical_k", "scripts", "tests", external=True)
    session.run("poetry", "run", "ruff", "check", "core", "fre", "historical_k", "scripts", "tests", "--select", "E,F,I", external=True)


@nox.session
def api_tests(session: nox.Session) -> None:
    """Run only API-focused tests for fast feedback."""
    session.run("poetry", "run", "pytest", "-q", "tests/test_api_*.py", external=True)
