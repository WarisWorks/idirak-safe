"""Verification for the single experimental model supported by this release."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from importlib import resources
import json
import os
from pathlib import Path
import stat
from typing import Any, Mapping, Sequence


SUPPORTED_MODEL = "lucio-xls-r-uyghur-cv7"
_MANIFEST_PACKAGE = "idirak_safe.model_manifests"
_DANGEROUS_SUFFIXES = {
    ".bat",
    ".bin",
    ".cmd",
    ".com",
    ".dll",
    ".dylib",
    ".exe",
    ".msi",
    ".pickle",
    ".pkl",
    ".ps1",
    ".pt",
    ".pth",
    ".py",
    ".sh",
    ".so",
}


class ModelVerificationError(RuntimeError):
    """Raised when a local model does not match the pinned manifest."""


@dataclass(frozen=True, slots=True)
class ManifestFile:
    path: str
    size: int
    sha256: str


@dataclass(frozen=True, slots=True)
class ModelManifest:
    model_id: str
    revision: str
    model_license: str
    training_data: str
    training_data_license: str
    files: tuple[ManifestFile, ...]


def _require_string(item: Mapping[str, Any], key: str) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value:
        raise ModelVerificationError(f"model manifest has invalid {key}")
    return value


def _parse_manifest(value: object) -> ModelManifest:
    if not isinstance(value, Mapping) or value.get("schema_version") != 1:
        raise ModelVerificationError("unsupported model manifest")
    raw_files = value.get("files")
    if not isinstance(raw_files, Sequence) or isinstance(raw_files, (str, bytes)):
        raise ModelVerificationError("model manifest has invalid files")

    parsed_files: list[ManifestFile] = []
    for raw_file in raw_files:
        if not isinstance(raw_file, Mapping):
            raise ModelVerificationError("model manifest has invalid file entry")
        path = _require_string(raw_file, "path")
        size = raw_file.get("size")
        sha256 = _require_string(raw_file, "sha256")
        if Path(path).name != path or not isinstance(size, int) or size < 0:
            raise ModelVerificationError("model manifest has invalid file metadata")
        if len(sha256) != 64 or any(char not in "0123456789abcdef" for char in sha256):
            raise ModelVerificationError("model manifest has invalid SHA-256")
        parsed_files.append(ManifestFile(path=path, size=size, sha256=sha256))

    if not parsed_files:
        raise ModelVerificationError("model manifest has no files")
    return ModelManifest(
        model_id=_require_string(value, "model_id"),
        revision=_require_string(value, "revision"),
        model_license=_require_string(value, "model_license"),
        training_data=_require_string(value, "training_data"),
        training_data_license=_require_string(value, "training_data_license"),
        files=tuple(parsed_files),
    )


def load_manifest(name: str = SUPPORTED_MODEL) -> ModelManifest:
    """Load a built-in, versioned model manifest."""

    if name != SUPPORTED_MODEL:
        raise ModelVerificationError(f"unsupported model: {name}")
    manifest_resource = resources.files(_MANIFEST_PACKAGE).joinpath(f"{name}.json")
    try:
        content = manifest_resource.read_text(encoding="utf-8")
        value = json.loads(content)
    except (OSError, json.JSONDecodeError) as error:
        raise ModelVerificationError("built-in model manifest is unreadable") from error
    return _parse_manifest(value)


def _hash_regular_file(path: Path, *, expected_size: int) -> str:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise ModelVerificationError(f"cannot open required model file: {path.name}") from error

    digest = hashlib.sha256()
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise ModelVerificationError(
                f"required model file is not a regular file: {path.name}"
            )
        if metadata.st_size != expected_size:
            raise ModelVerificationError(f"model file has wrong size: {path.name}")
        with os.fdopen(descriptor, "rb", closefd=False) as handle:
            while chunk := handle.read(1024 * 1024):
                digest.update(chunk)
    finally:
        os.close(descriptor)
    return digest.hexdigest()


def verify_model_directory(
    model_dir: str | Path,
    *,
    manifest: ModelManifest | None = None,
) -> ModelManifest:
    """Verify a local model before any audio is opened or inference is started."""

    directory = Path(model_dir)
    if directory.is_symlink():
        raise ModelVerificationError("model directory must not be a symbolic link")
    if not directory.is_dir():
        raise ModelVerificationError("model directory does not exist")

    selected_manifest = manifest or load_manifest()
    try:
        entries = tuple(directory.iterdir())
    except OSError as error:
        raise ModelVerificationError("model directory cannot be read") from error

    expected_names = {expected.path for expected in selected_manifest.files}
    for entry in entries:
        if entry.is_symlink():
            raise ModelVerificationError("model directory contains a symbolic link")
        if entry.name == ".cache":
            if not entry.is_dir():
                raise ModelVerificationError(
                    "model directory contains an invalid cache entry"
                )
            continue
        if entry.is_file():
            if entry.suffix.lower() in _DANGEROUS_SUFFIXES:
                raise ModelVerificationError(
                    f"model directory contains an unsafe file type: {entry.name}"
                )
            if os.name == "posix" and entry.stat(follow_symlinks=False).st_mode & 0o111:
                raise ModelVerificationError(
                    f"model directory contains an executable file: {entry.name}"
                )
        else:
            raise ModelVerificationError(
                f"model directory contains an unexpected entry: {entry.name}"
            )
        if entry.name not in expected_names:
            raise ModelVerificationError(
                f"model directory contains an unexpected entry: {entry.name}"
            )

    for expected in selected_manifest.files:
        model_file = directory / expected.path
        actual_sha256 = _hash_regular_file(model_file, expected_size=expected.size)
        if actual_sha256 != expected.sha256:
            raise ModelVerificationError(
                f"model file failed SHA-256 verification: {expected.path}"
            )
    return selected_manifest
