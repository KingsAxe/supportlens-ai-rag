"""I/O helpers for ingestion data files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


def get_repo_root() -> Path:
    """Return the repository root based on this module location."""
    return Path(__file__).resolve().parents[2]


def resolve_repo_path(*parts: str) -> Path:
    """Resolve a path relative to the repository root."""
    return get_repo_root().joinpath(*parts)


def ensure_parent_dir(path: Path) -> None:
    """Create the parent directory for a file path if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    """Read a JSONL file with line-aware error messages."""
    file_path = Path(path)
    records: list[dict[str, Any]] = []

    try:
        with file_path.open("r", encoding="utf-8") as handle:
            for line_number, raw_line in enumerate(handle, start=1):
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    parsed = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"Invalid JSONL in {file_path} at line {line_number}: {exc.msg}"
                    ) from exc
                if not isinstance(parsed, dict):
                    raise ValueError(
                        f"Invalid JSONL in {file_path} at line {line_number}: expected object"
                    )
                records.append(parsed)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"JSONL file not found: {file_path}") from exc

    return records


def write_jsonl(path: str | Path, records: Iterable[dict[str, Any]]) -> None:
    """Write dictionaries to a JSONL file."""
    file_path = Path(path)
    ensure_parent_dir(file_path)
    with file_path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=True) + "\n")


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    """Write a JSON object with stable formatting."""
    file_path = Path(path)
    ensure_parent_dir(file_path)
    with file_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=True)
        handle.write("\n")