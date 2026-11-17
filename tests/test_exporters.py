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

    def _forged(self) -> Transcript:
        return Transcript.from_mapping(
            {
                "segments": [
                    {
                        "start": 0,
                        "end": 1,
                        "text": "real\n\n2\n00:00:05,000 --> 00:00:09,000\nforged",
                        "speaker": "A <b>",
                    }
                ]
            }
        )

    def test_srt_text_cannot_forge_an_extra_cue(self) -> None:
        rendered = export_srt(self._forged())
        self.assertEqual(rendered.count("\n\n"), 0)
        self.assertTrue(rendered.startswith("1\n00:00:00,000 --> 00:00:01,000\n"))

    def test_vtt_escapes_markup_and_cue_arrows(self) -> None:
        rendered = export_vtt(self._forged())
        body = rendered.removeprefix("WEBVTT\n\n")
        self.assertEqual(body.count("\n\n"), 0)
        self.assertEqual(body.count("-->"), 1)
        self.assertIn("A &lt;b&gt;: real", body)
        self.assertIn("00:00:05,000 --&gt; 00:00:09,000", body)

    def test_vtt_escapes_ampersand_first(self) -> None:
        transcript = Transcript.from_mapping(
            {"segments": [{"start": 0, "end": 1, "text": "a & b &lt; c"}]}
        )
        self.assertIn("a &amp; b &amp;lt; c", export_vtt(transcript))

    def test_txt_keeps_one_segment_per_line(self) -> None:
        self.assertEqual(
            export_txt(self._forged()),
            "A <b>: real 2 00:00:05,000 --> 00:00:09,000 forged\n",
        )


if __name__ == "__main__":
    unittest.main()
