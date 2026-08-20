import json
import unittest

from idirak_safe.exporters import (
    export_json,
    export_srt,
    export_transcript,
    export_txt,
    export_vtt,
)
from idirak_safe.model import Transcript


class ExporterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.transcript = Transcript.from_mapping(
            {
                "language": "ug",
                "source": "synthetic example",
                "segments": [
                    {"start": 0, "end": 1.5, "text": "ياخشىمۇسىز."},
                    {
                        "start": 61.234,
                        "end": 62.5,
                        "text": "ياخشى، رەھمەت.",
                        "speaker": "Speaker 2",
                    },
                ],
            }
        )

    def test_txt(self) -> None:
        self.assertEqual(
            export_txt(self.transcript),
            "ياخشىمۇسىز.\nSpeaker 2: ياخشى، رەھمەت.\n",
        )

    def test_srt(self) -> None:
        self.assertEqual(
            export_srt(self.transcript),
            "1\n"
            "00:00:00,000 --> 00:00:01,500\n"
            "ياخشىمۇسىز.\n\n"
            "2\n"
            "00:01:01,234 --> 00:01:02,500\n"
            "Speaker 2: ياخشى، رەھمەت.\n",
        )

    def test_vtt(self) -> None:
        self.assertTrue(export_vtt(self.transcript).startswith("WEBVTT\n\n"))
        self.assertIn("00:01:01.234 --> 00:01:02.500", export_vtt(self.transcript))

    def test_json_preserves_unicode_and_is_valid(self) -> None:
        rendered = export_json(self.transcript)
        self.assertIn("ياخشىمۇسىز", rendered)
        self.assertEqual(json.loads(rendered)["language"], "ug")

    def test_unknown_format(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported export format"):
            export_transcript(self.transcript, "docx")


if __name__ == "__main__":
    unittest.main()
