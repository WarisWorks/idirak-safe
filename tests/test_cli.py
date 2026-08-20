from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
import unittest

from idirak_safe.cli import main


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
        self.assertIn("Not implemented: speech recognition (ASR)", output.getvalue())
        self.assertIn("Network and telemetry: none", output.getvalue())

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

    def test_transcribe_reports_unimplemented_feature(self) -> None:
        error_output = StringIO()
        with redirect_stderr(error_output):
            status = main(["transcribe"])
        self.assertEqual(status, 2)
        self.assertIn("ASR is not implemented", error_output.getvalue())

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
