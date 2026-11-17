"""Small local-file helpers with safe defaults."""

from __future__ import annotations

import os
from pathlib import Path
import tempfile


def _sync_directory(directory: Path) -> None:
    """Best-effort flush of a directory entry; unsupported on some platforms."""

    try:
        descriptor = os.open(directory, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    except OSError:
        pass
    finally:
        os.close(descriptor)


def _publish_without_replacing(temporary: Path, target: Path) -> None:
    """Move a finished temporary file to ``target`` only if it does not exist."""

    exists_message = f"output already exists: {target}; pass --force to replace it"
    try:
        os.link(temporary, target)
        return
    except FileExistsError as error:
        raise FileExistsError(exists_message) from error
    except OSError:
        # Hard links are unavailable on some filesystems, such as FAT/exFAT
        # removable drives. Fall back to an exclusive reservation below.
        pass

    try:
        descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as error:
        raise FileExistsError(exists_message) from error
    os.close(descriptor)
    try:
        os.replace(temporary, target)
    except BaseException:
        # Only the empty reservation created above is removed here.
        try:
            os.unlink(target)
        except OSError:
            pass
        raise


def atomic_write_text(
    path: str | Path,
    content: str,
    *,
    overwrite: bool = False,
) -> None:
    """Atomically write UTF-8 text in an existing local directory.

    New files inherit the private permissions of ``mkstemp``. Existing files
    are never replaced unless ``overwrite`` is explicitly enabled. The complete
    content is flushed to a same-directory temporary file first, so a failure
    never leaves a partial transcript at ``path``.
    """

    target = Path(path)
    parent = target.parent
    if not parent.is_dir():
        raise FileNotFoundError(f"output directory does not exist: {parent}")
    if target.is_dir():
        raise IsADirectoryError(f"output path is a directory: {target}")

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
            _publish_without_replacing(temporary, target)
        _sync_directory(parent)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
