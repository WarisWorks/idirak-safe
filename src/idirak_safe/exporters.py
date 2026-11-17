"""Deterministic, offline exporters for validated transcripts."""

from __future__ import annotations

import json
from typing import Callable

from .model import Segment, Transcript


def _visible_lines(segment: Segment) -> list[str]:
    """Return the non-blank lines of a segment, prefixed with its speaker.

    Blank lines are dropped because SRT and WebVTT use them to end a cue; text
    containing one could otherwise be read as an additional, forged cue.
    """

    lines = [line.strip() for line in segment.text.splitlines()]
    lines = [line for line in lines if line]
    if segment.speaker is not None:
        lines[0] = f"{segment.speaker.strip()}: {lines[0]}"
    return lines


def _escape_vtt(line: str) -> str:
    """Escape WebVTT markup so text is shown literally, including ``-->``."""

    return line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def export_txt(transcript: Transcript) -> str:
    """Render one transcript segment per line."""

    return (
        "\n".join(" ".join(_visible_lines(segment)) for segment in transcript.segments)
        + "\n"
    )


def _timestamp(seconds: float, *, decimal_separator: str) -> str:
    milliseconds = int(round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    whole_seconds, millis = divmod(remainder, 1000)
    return (
        f"{hours:02d}:{minutes:02d}:{whole_seconds:02d}"
        f"{decimal_separator}{millis:03d}"
    )


def export_srt(transcript: Transcript) -> str:
    """Render SubRip subtitles."""

    cues: list[str] = []
    for index, segment in enumerate(transcript.segments, start=1):
        start = _timestamp(segment.start, decimal_separator=",")
        end = _timestamp(segment.end, decimal_separator=",")
        text = "\n".join(_visible_lines(segment))
        cues.append(f"{index}\n{start} --> {end}\n{text}")
    return "\n\n".join(cues) + "\n"


def export_vtt(transcript: Transcript) -> str:
    """Render WebVTT subtitles."""

    cues: list[str] = []
    for segment in transcript.segments:
        start = _timestamp(segment.start, decimal_separator=".")
        end = _timestamp(segment.end, decimal_separator=".")
        text = "\n".join(_escape_vtt(line) for line in _visible_lines(segment))
        cues.append(f"{start} --> {end}\n{text}")
    return "WEBVTT\n\n" + "\n\n".join(cues) + "\n"


def export_json(transcript: Transcript) -> str:
    """Render normalized UTF-8 JSON without escaping Uyghur text."""

    return json.dumps(
        transcript.to_mapping(), ensure_ascii=False, indent=2, sort_keys=False
    ) + "\n"


EXPORTERS: dict[str, Callable[[Transcript], str]] = {
    "txt": export_txt,
    "srt": export_srt,
    "vtt": export_vtt,
    "json": export_json,
}


def export_transcript(transcript: Transcript, output_format: str) -> str:
    """Render a transcript using a supported output format."""

    try:
        exporter = EXPORTERS[output_format]
    except KeyError as error:
        supported = ", ".join(EXPORTERS)
        raise ValueError(
            f"unsupported export format {output_format!r}; choose one of: {supported}"
        ) from error
    return exporter(transcript)
