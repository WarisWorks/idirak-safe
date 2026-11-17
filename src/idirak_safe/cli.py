"""Truthful local-only command-line interface for the pre-alpha."""

from __future__ import annotations

import argparse
from importlib import util as importlib_util
from pathlib import Path
import sys
from typing import Sequence

from . import __version__
from .asr import ASRError, create_backend
from .audio import AudioValidationError
from .exporters import EXPORTERS, export_transcript
from .model import Transcript, TranscriptValidationError
from .model_files import ModelVerificationError, load_manifest, verify_model_directory
from .storage import atomic_write_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="idirak-safe",
        description=(
            "Pre-alpha local transcript tools with an optional experimental, "
            "offline-only Uyghur ASR backend."
        ),
    )
    parser.add_argument(
        "--version", action="version", version=f"idirak-safe {__version__}"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "doctor", help="show the implemented and unimplemented pre-alpha features"
    )

    export_parser = subparsers.add_parser(
        "export", help="convert an existing local transcript JSON file"
    )
    export_parser.add_argument("input", type=Path, help="local transcript JSON file")
    export_parser.add_argument(
        "--format",
        required=True,
        choices=tuple(EXPORTERS),
        dest="output_format",
        help="output format",
    )
    export_parser.add_argument(
        "--output", required=True, type=Path, help="local output file"
    )
    export_parser.add_argument(
        "--force", action="store_true", help="replace an existing output file"
    )

    verify_parser = subparsers.add_parser(
        "verify-model", help="verify the pinned experimental model without opening audio"
    )
    verify_parser.add_argument(
        "--model-dir", required=True, type=Path, help="local model directory"
    )

    transcribe_parser = subparsers.add_parser(
        "transcribe", help="run the explicit experimental local ASR backend"
    )
    transcribe_parser.add_argument("input", type=Path, help="local PCM WAV file")
    transcribe_parser.add_argument(
        "--backend", required=True, choices=("hf-wav2vec2",), help="local backend"
    )
    transcribe_parser.add_argument(
        "--model-dir", required=True, type=Path, help="verified local model directory"
    )
    transcribe_parser.add_argument(
        "--format",
        required=True,
        choices=tuple(EXPORTERS),
        dest="output_format",
        help="output format",
    )
    transcribe_parser.add_argument(
        "--output", required=True, type=Path, help="local output file"
    )
    transcribe_parser.add_argument(
        "--force", action="store_true", help="replace an existing output file"
    )
    return parser


_ASR_MODULES = ("numpy", "safetensors", "torch", "transformers")


def _missing_asr_modules() -> list[str]:
    """Look up optional ASR packages without importing or running them."""

    missing: list[str] = []
    for name in _ASR_MODULES:
        try:
            found = importlib_util.find_spec(name) is not None
        except (ImportError, ValueError):
            found = False
        if not found:
            missing.append(name)
    return missing


def _doctor() -> int:
    manifest = load_manifest()
    missing = _missing_asr_modules()
    print(f"Idirak Safe {__version__} (pre-alpha)")
    print("Implemented: local transcript validation and TXT/SRT/VTT/JSON export")
    print("Experimental: verified local Wav2Vec2 ASR for short strict PCM WAV input")
    print(f"Pinned model: {manifest.model_id} at revision {manifest.revision}")
    if missing:
        print(
            f"ASR dependencies: not found: {', '.join(missing)} "
            "(install with: pip install -e '.[asr]')"
        )
    else:
        print("ASR dependencies: found (not loaded or tested by this check)")
    print("Runtime policy: offline-only; no upload, model download, or telemetry path")
    print("Sensitive-use status: NOT READY; use only non-sensitive test audio")
    return 0


def _export(input_path: Path, output_path: Path, output_format: str, force: bool) -> int:
    transcript = Transcript.load(input_path)
    rendered = export_transcript(transcript, output_format)
    atomic_write_text(output_path, rendered, overwrite=force)
    print(f"Exported {len(transcript.segments)} segment(s) to {output_path.name}")
    return 0


def _same_path(first: Path, second: Path) -> bool:
    try:
        return first.resolve(strict=False) == second.resolve(strict=False)
    except OSError:
        return first.absolute() == second.absolute()


def _transcribe(
    input_path: Path,
    *,
    backend_name: str,
    model_dir: Path,
    output_path: Path,
    output_format: str,
    force: bool,
) -> int:
    if _same_path(input_path, output_path):
        raise ValueError("audio input and transcript output must be different files")
    backend = create_backend(backend_name, model_dir=model_dir)
    transcript = backend.transcribe(input_path)
    rendered = export_transcript(transcript, output_format)
    atomic_write_text(output_path, rendered, overwrite=force)
    print(f"Created an experimental draft transcript at {output_path.name}")
    print("Human review against the audio is required before any consequential use.")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    arguments = parser.parse_args(argv)

    try:
        if arguments.command == "doctor":
            return _doctor()
        if arguments.command == "export":
            return _export(
                arguments.input,
                arguments.output,
                arguments.output_format,
                arguments.force,
            )
        if arguments.command == "verify-model":
            manifest = verify_model_directory(arguments.model_dir)
            print(
                "Verified supported model: "
                f"{manifest.model_id} at revision {manifest.revision}"
            )
            return 0
        if arguments.command == "transcribe":
            return _transcribe(
                arguments.input,
                backend_name=arguments.backend,
                model_dir=arguments.model_dir,
                output_path=arguments.output,
                output_format=arguments.output_format,
                force=arguments.force,
            )
    except (
        ASRError,
        AudioValidationError,
        ModelVerificationError,
        OSError,
        TranscriptValidationError,
        ValueError,
    ) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("error: interrupted", file=sys.stderr)
        return 130

    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
