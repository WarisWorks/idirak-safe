"""Validated transcript data structures.

The pre-alpha deliberately accepts a small, documented JSON shape. Keeping the
model narrow makes local exports predictable and avoids silently accepting
fields that may contain sensitive data.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence


class TranscriptValidationError(ValueError):
    """Raised when transcript data does not match the supported local schema."""


def _require_mapping(value: object, *, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TranscriptValidationError(f"{field} must be a JSON object")
    return value


def _require_text(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TranscriptValidationError(f"{field} must be a non-empty string")
    return value


def _require_seconds(value: object, *, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TranscriptValidationError(f"{field} must be a number of seconds")
    seconds = float(value)
    if not math.isfinite(seconds) or seconds < 0:
        raise TranscriptValidationError(
            f"{field} must be a finite, non-negative number of seconds"
        )
    return seconds


@dataclass(frozen=True, slots=True)
class Segment:
    """One timestamped section of an existing transcript."""

    start: float
    end: float
    text: str
    speaker: str | None = None

    @classmethod
    def from_mapping(cls, value: object, *, index: int) -> "Segment":
        item = _require_mapping(value, field=f"segments[{index}]")
        allowed = {"start", "end", "text", "speaker"}
        unknown = sorted(set(item) - allowed)
        if unknown:
            raise TranscriptValidationError(
                f"segments[{index}] has unsupported field(s): {', '.join(unknown)}"
            )

        start = _require_seconds(item.get("start"), field=f"segments[{index}].start")
        end = _require_seconds(item.get("end"), field=f"segments[{index}].end")
        if end < start:
            raise TranscriptValidationError(
                f"segments[{index}].end must be greater than or equal to start"
            )

        text = _require_text(item.get("text"), field=f"segments[{index}].text")
        speaker_value = item.get("speaker")
        speaker = None
        if speaker_value is not None:
            speaker = _require_text(
                speaker_value, field=f"segments[{index}].speaker"
            )
        return cls(start=start, end=end, text=text, speaker=speaker)

    def to_mapping(self) -> dict[str, object]:
        result: dict[str, object] = {
            "start": self.start,
            "end": self.end,
            "text": self.text,
        }
        if self.speaker is not None:
            result["speaker"] = self.speaker
        return result


@dataclass(frozen=True, slots=True)
class Transcript:
    """A locally loaded transcript that is ready for deterministic export."""

    segments: tuple[Segment, ...]
    language: str = "ug"
    source: str | None = None

    @classmethod
    def from_mapping(cls, value: object) -> "Transcript":
        item = _require_mapping(value, field="transcript")
        allowed = {"language", "source", "segments"}
        unknown = sorted(set(item) - allowed)
        if unknown:
            raise TranscriptValidationError(
                f"transcript has unsupported field(s): {', '.join(unknown)}"
            )

        language = _require_text(item.get("language", "ug"), field="language")
        source_value = item.get("source")
        source = None
        if source_value is not None:
            source = _require_text(source_value, field="source")

        segment_values = item.get("segments")
        if (
            not isinstance(segment_values, Sequence)
            or isinstance(segment_values, (str, bytes, bytearray))
            or not segment_values
        ):
            raise TranscriptValidationError("segments must be a non-empty JSON array")

        segments = tuple(
            Segment.from_mapping(segment, index=index)
            for index, segment in enumerate(segment_values)
        )
        for index in range(1, len(segments)):
            if segments[index].start < segments[index - 1].start:
                raise TranscriptValidationError(
                    "segments must be ordered by non-decreasing start time"
                )
        return cls(segments=segments, language=language, source=source)

    @classmethod
    def from_json(cls, text: str) -> "Transcript":
        try:
            value = json.loads(text)
        except json.JSONDecodeError as error:
            raise TranscriptValidationError(
                f"invalid transcript JSON at line {error.lineno}, column {error.colno}"
            ) from error
        return cls.from_mapping(value)

    @classmethod
    def load(cls, path: str | Path) -> "Transcript":
        """Read and validate a UTF-8 transcript from a local file."""

        return cls.from_json(Path(path).read_text(encoding="utf-8"))

    def to_mapping(self) -> dict[str, object]:
        result: dict[str, object] = {
            "language": self.language,
            "segments": [segment.to_mapping() for segment in self.segments],
        }
        if self.source is not None:
            result["source"] = self.source
        return result
