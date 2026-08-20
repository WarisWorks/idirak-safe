"""Small local-file helpers with safe defaults."""

from __future__ import annotations

import os
from pathlib import Path
import tempfile


def atomic_write_text(
    path: str | Path,
    content: str,
    *,
    overwrite: bool = False,
) -> None:
    """Atomically write UTF-8 text in an existing local directory.

    New files inherit the private permissions of ``mkstemp``. Existing files
    are never replaced unless ``overwrite`` is explicitly enabled.
    """

    target = Path(path)
    parent = target.parent
    if not parent.is_dir():
        raise FileNotFoundError(f"output directory does not exist: {parent}")

    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{target.name}.", suffix=".tmp", dir=parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())

        if overwrite:
            os.replace(temporary, target)
        else:
            try:
                os.link(temporary, target)
            except FileExistsError as error:
                raise FileExistsError(
                    f"output already exists: {target}; pass --force to replace it"
                ) from error
            temporary.unlink()
    finally:
        if temporary.exists():
            temporary.unlink()
