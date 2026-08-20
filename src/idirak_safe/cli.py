"""Truthful local-only command-line interface for the pre-alpha."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Sequence

from .exporters import EXPORTERS, export_transcript
from .model import Transcript, TranscriptValidationError
from .storage import atomic_write_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="idirak-safe",
        description=(
            "Pre-alpha local transcript validation and export tools. "
            "This build does not perform speech recognition."
        ),
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

    subparsers.add_parser(
        "transcribe", help="report that ASR is not implemented in this pre-alpha"
    )
    return parser


def _doctor() -> int:
    print("Idirak Safe 0.1.0a0 (pre-alpha)")
    print("Implemented: local transcript JSON validation and TXT/SRT/VTT/JSON export")
    print("Not implemented: speech recognition (ASR)")
    print("Network and telemetry: none")
    return 0


def _export(input_path: Path, output_path: Path, output_format: str, force: bool) -> int:
    transcript = Transcript.load(input_path)
    rendered = export_transcript(transcript, output_format)
    atomic_write_text(output_path, rendered, overwrite=force)
    print(f"Exported {len(transcript.segments)} segment(s) to {output_path}")
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
        if arguments.command == "transcribe":
            print(
                "error: ASR is not implemented in this pre-alpha; "
                "only existing local transcript JSON can be validated and exported",
                file=sys.stderr,
            )
            return 2
    except (OSError, TranscriptValidationError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
