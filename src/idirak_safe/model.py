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
import unicodedata


MAX_TRANSCRIPT_BYTES = 8 * 1024 * 1024
_TEXT_LINE_BREAKS = frozenset("\n\r\t")


class TranscriptValidationError(ValueError):
    """Raised when transcript data does not match the supported local schema."""


def _require_mapping(value: object, *, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TranscriptValidationError(f"{field} must be a JSON object")
    return value


def _require_text(value: object, *, field: str, multiline: bool = False) -> str:
    """Require visible text without control or unpaired surrogate characters.

    Control characters could forge extra subtitle cues, hide content from a
    reviewer, or make an export unreadable, so they are rejected rather than
    silently rewritten. Only segment text may contain tabs and line breaks.
    """

    if not isinstance(value, str) or not value.strip():
        raise TranscriptValidationError(f"{field} must be a non-empty string")
    for character in value:
        category = unicodedata.category(character)
        if category == "Cs" or (
            category == "Cc"
            and not (multiline and character in _TEXT_LINE_BREAKS)
        ):
            raise TranscriptValidationError(
                f"{field} contains an unsupported control character"
            )
    return value


def _require_seconds(value: object, *, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TranscriptValidationError(f"{field} must be a number of seconds")
    try:
        seconds = float(value)
    except OverflowError:
        seconds = math.inf
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

    def __post_init__(self) -> None:
        # Segments built directly in code, for example by an ASR backend, get
        # the same checks as segments parsed from JSON.
        start = _require_seconds(self.start, field="segment start")
        end = _require_seconds(self.end, field="segment end")
        if end < start:
            raise TranscriptValidationError(
                "segment end must be greater than or equal to start"
            )
        _require_text(self.text, field="segment text", multiline=True)
        if self.speaker is not None:
            _require_text(self.speaker, field="segment speaker")
        object.__setattr__(self, "start", start)
        object.__setattr__(self, "end", end)

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

        text = _require_text(
            item.get("text"), field=f"segments[{index}].text", multiline=True
        )
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

    def __post_init__(self) -> None:
        segments = tuple(self.segments)
        if not segments or not all(isinstance(item, Segment) for item in segments):
            raise TranscriptValidationError(
                "segments must be a non-empty sequence of segments"
            )
        for index in range(1, len(segments)):
            if segments[index].start < segments[index - 1].start:
                raise TranscriptValidationError(
                    "segments must be ordered by non-decreasing start time"
                )
        _require_text(self.language, field="language")
        if self.source is not None:
            _require_text(self.source, field="source")
        object.__setattr__(self, "segments", segments)

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
        return cls(segments=segments, language=language, source=source)

    @classmethod
    def from_json(cls, text: str) -> "Transcript":
        try:
            value = json.loads(text)
        except json.JSONDecodeError as error:
            raise TranscriptValidationError(
                f"invalid transcript JSON at line {error.lineno}, column {error.colno}"
            ) from error
        except RecursionError as error:
            raise TranscriptValidationError(
                "transcript JSON is nested too deeply"
            ) from error
        return cls.from_mapping(value)

    @classmethod
    def load(cls, path: str | Path) -> "Transcript":
        """Read and validate a bounded UTF-8 transcript from a local file."""

        with Path(path).open("rb") as handle:
            data = handle.read(MAX_TRANSCRIPT_BYTES + 1)
        if len(data) > MAX_TRANSCRIPT_BYTES:
            raise TranscriptValidationError(
                "transcript file exceeds the 8 MiB safety limit"
            )
        try:
            # ``utf-8-sig`` also accepts the byte-order mark some editors add.
            text = data.decode("utf-8-sig")
        except UnicodeDecodeError as error:
            raise TranscriptValidationError(
                "transcript file is not valid UTF-8 text"
            ) from error
        return cls.from_json(text)

    def to_mapping(self) -> dict[str, object]:
        result: dict[str, object] = {
            "language": self.language,
            "segments": [segment.to_mapping() for segment in self.segments],
        }
        if self.source is not None:
            result["source"] = self.source
        return result
