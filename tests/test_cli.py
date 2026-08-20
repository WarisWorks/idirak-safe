from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from idirak_safe.cli import main
from idirak_safe.model import Segment, Transcript


SAMPLE = """{
  "language": "ug",
  "segments": [
    {"start": 0, "end": 1.5, "text": "ياخشىمۇسىز."}
  ]
}
"""


class CliTests(unittest.TestCase):
    def test_doctor_is_truthful_about_scope(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            status = main(["doctor"])
        self.assertEqual(status, 0)
        self.assertIn("Experimental", output.getvalue())
        self.assertIn("offline-only", output.getvalue())
        self.assertIn("NOT READY", output.getvalue())

    def test_export_writes_local_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "input.json"
            output_path = Path(directory) / "output.vtt"
            input_path.write_text(SAMPLE, encoding="utf-8")

            output = StringIO()
            with redirect_stdout(output):
                status = main(
                    [
                        "export",
                        str(input_path),
                        "--format",
                        "vtt",
                        "--output",
                        str(output_path),
                    ]
                )

            self.assertEqual(status, 0)
            self.assertTrue(output_path.read_text(encoding="utf-8").startswith("WEBVTT"))
            self.assertIn("1 segment(s)", output.getvalue())

    def test_transcribe_uses_explicit_backend_and_writes_output(self) -> None:
        transcript = Transcript(
            language="ug",
            segments=(Segment(start=0, end=1, text="ياخشىمۇسىز"),),
        )
        backend = MagicMock()
        backend.transcribe.return_value = transcript
        with tempfile.TemporaryDirectory() as directory:
            audio = Path(directory) / "audio.wav"
            output_path = Path(directory) / "transcript.json"
            audio.write_bytes(b"placeholder")
            output = StringIO()
            with (
                patch("idirak_safe.cli.create_backend", return_value=backend) as create,
                redirect_stdout(output),
            ):
                status = main(
                    [
                        "transcribe",
                        str(audio),
                        "--backend",
                        "hf-wav2vec2",
                        "--model-dir",
                        str(Path(directory) / "model"),
                        "--format",
                        "json",
                        "--output",
                        str(output_path),
                    ]
                )

            self.assertEqual(status, 0)
            self.assertIn("ياخشىمۇسىز", output_path.read_text(encoding="utf-8"))
            self.assertNotIn(str(output_path.parent), output.getvalue())
            create.assert_called_once()

    def test_transcribe_never_replaces_audio_input(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            audio = Path(directory) / "audio.wav"
            audio.write_bytes(b"original")
            error_output = StringIO()
            with redirect_stderr(error_output):
                status = main(
                    [
                        "transcribe",
                        str(audio),
                        "--backend",
                        "hf-wav2vec2",
                        "--model-dir",
                        str(Path(directory) / "model"),
                        "--format",
                        "json",
                        "--output",
                        str(audio),
                        "--force",
                    ]
                )
            self.assertEqual(status, 2)
            self.assertEqual(audio.read_bytes(), b"original")
            self.assertIn("must be different", error_output.getvalue())

    def test_backend_failure_leaves_no_output(self) -> None:
        backend = MagicMock()
        backend.transcribe.side_effect = OSError("inference failed")
        with tempfile.TemporaryDirectory() as directory:
            audio = Path(directory) / "audio.wav"
            output_path = Path(directory) / "transcript.json"
            audio.write_bytes(b"placeholder")
            with (
                patch("idirak_safe.cli.create_backend", return_value=backend),
                redirect_stderr(StringIO()),
            ):
                status = main(
                    [
                        "transcribe",
                        str(audio),
                        "--backend",
                        "hf-wav2vec2",
                        "--model-dir",
                        str(Path(directory) / "model"),
                        "--format",
                        "json",
                        "--output",
                        str(output_path),
                    ]
                )
            self.assertEqual(status, 2)
            self.assertFalse(output_path.exists())

    def test_invalid_input_returns_error_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "input.json"
            output_path = Path(directory) / "output.txt"
            input_path.write_text("not json", encoding="utf-8")

            error_output = StringIO()
            with redirect_stderr(error_output):
                status = main(
                    [
                        "export",
                        str(input_path),
                        "--format",
                        "txt",
                        "--output",
                        str(output_path),
                    ]
                )

            self.assertEqual(status, 2)
            self.assertIn("invalid transcript JSON", error_output.getvalue())
            self.assertFalse(output_path.exists())


if __name__ == "__main__":
    unittest.main()
