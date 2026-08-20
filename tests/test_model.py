import unittest

from idirak_safe.model import Transcript, TranscriptValidationError


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


if __name__ == "__main__":
    unittest.main()
