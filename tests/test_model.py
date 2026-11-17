from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from idirak_safe.model import Segment, Transcript, TranscriptValidationError


class TranscriptModelTests(unittest.TestCase):
    def test_loads_supported_shape_and_defaults_language(self) -> None:
        transcript = Transcript.from_mapping(
            {
                "segments": [
                    {"start": 0, "end": 1.25, "text": "ياخشىمۇسىز."},
                    {
                        "start": 1.25,
                        "end": 3,
                        "text": "ياخشى، رەھمەت.",
                        "speaker": "Speaker 2",
                    },
                ]
            }
        )

        self.assertEqual(transcript.language, "ug")
        self.assertEqual(len(transcript.segments), 2)
        self.assertEqual(transcript.segments[1].speaker, "Speaker 2")

    def test_rejects_unknown_fields(self) -> None:
        with self.assertRaisesRegex(TranscriptValidationError, "unsupported field"):
            Transcript.from_mapping(
                {
                    "segments": [
                        {"start": 0, "end": 1, "text": "test", "secret": "value"}
                    ]
                }
            )

    def test_rejects_invalid_timestamps(self) -> None:
        with self.assertRaisesRegex(TranscriptValidationError, "greater than or equal"):
            Transcript.from_mapping(
                {"segments": [{"start": 2, "end": 1, "text": "test"}]}
            )

    def test_rejects_out_of_order_segments(self) -> None:
        with self.assertRaisesRegex(TranscriptValidationError, "ordered"):
            Transcript.from_mapping(
                {
                    "segments": [
                        {"start": 2, "end": 3, "text": "second"},
                        {"start": 1, "end": 2, "text": "first"},
                    ]
                }
            )

    def test_json_error_does_not_echo_input(self) -> None:
        sensitive_text = '{"segments": ["private words"}'
        with self.assertRaises(TranscriptValidationError) as context:
            Transcript.from_json(sensitive_text)
        self.assertNotIn("private words", str(context.exception))

    def test_rejects_control_characters(self) -> None:
        for field, value in (
            ("text", "hidden\x00text"),
            ("text", "escape\x1b[2J"),
            ("speaker", "Speaker\n00:00:00,000 --> 00:00:09,000"),
        ):
            segment = {"start": 0, "end": 1, "text": "test"}
            segment[field] = value
            with self.subTest(field=field):
                with self.assertRaisesRegex(
                    TranscriptValidationError, "control character"
                ):
                    Transcript.from_mapping({"segments": [segment]})

    def test_segment_text_may_span_lines(self) -> None:
        transcript = Transcript.from_mapping(
            {"segments": [{"start": 0, "end": 1, "text": "first\r\nsecond\tline"}]}
        )
        self.assertEqual(transcript.segments[0].text, "first\r\nsecond\tline")

    def test_rejects_unpaired_surrogate(self) -> None:
        with self.assertRaisesRegex(TranscriptValidationError, "control character"):
            Transcript.from_json(
                '{"segments": [{"start": 0, "end": 1, "text": "a\\ud800"}]}'
            )

    def test_oversized_number_is_a_validation_error(self) -> None:
        huge = "1" + "0" * 400
        with self.assertRaisesRegex(TranscriptValidationError, "finite"):
            Transcript.from_json(
                '{"segments": [{"start": 0, "end": %s, "text": "test"}]}' % huge
            )

    def test_deeply_nested_json_is_a_validation_error(self) -> None:
        with self.assertRaises(TranscriptValidationError):
            Transcript.from_json("[" * 200_000)

    def test_direct_construction_is_validated(self) -> None:
        with self.assertRaisesRegex(TranscriptValidationError, "non-empty string"):
            Segment(start=0, end=1, text="   ")
        with self.assertRaisesRegex(TranscriptValidationError, "greater than or equal"):
            Segment(start=2, end=1, text="test")
        with self.assertRaisesRegex(TranscriptValidationError, "finite"):
            Segment(start=0, end=float("nan"), text="test")
        with self.assertRaisesRegex(TranscriptValidationError, "non-empty sequence"):
            Transcript(segments=())
        with self.assertRaisesRegex(TranscriptValidationError, "ordered"):
            Transcript(
                segments=(
                    Segment(start=2, end=3, text="second"),
                    Segment(start=1, end=2, text="first"),
                )
            )

    def test_direct_construction_normalizes_types(self) -> None:
        transcript = Transcript(segments=[Segment(start=0, end=1, text="test")])
        self.assertIsInstance(transcript.segments, tuple)
        self.assertIsInstance(transcript.segments[0].start, float)

    def test_load_accepts_byte_order_mark(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "transcript.json"
            path.write_bytes(
                b"\xef\xbb\xbf"
                + '{"segments": [{"start": 0, "end": 1, "text": "سالام"}]}'.encode()
            )
            self.assertEqual(Transcript.load(path).segments[0].text, "سالام")

    def test_load_rejects_non_utf8_and_oversized_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "transcript.json"
            path.write_bytes(b"\xff\xfe{}")
            with self.assertRaisesRegex(TranscriptValidationError, "UTF-8"):
                Transcript.load(path)
            with patch("idirak_safe.model.MAX_TRANSCRIPT_BYTES", 16):
                path.write_bytes(b" " * 17)
                with self.assertRaisesRegex(TranscriptValidationError, "safety limit"):
                    Transcript.load(path)


if __name__ == "__main__":
    unittest.main()
