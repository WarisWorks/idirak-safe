from pathlib import Path
import tempfile
import unittest

from idirak_safe.storage import atomic_write_text


class AtomicWriteTests(unittest.TestCase):
    def test_writes_utf8_text(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "output.txt"
            atomic_write_text(output, "ئۇيغۇرچە\n")
            self.assertEqual(output.read_text(encoding="utf-8"), "ئۇيغۇرچە\n")

    def test_does_not_replace_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "output.txt"
            output.write_text("original", encoding="utf-8")

            with self.assertRaisesRegex(FileExistsError, "--force"):
                atomic_write_text(output, "replacement")

            self.assertEqual(output.read_text(encoding="utf-8"), "original")

    def test_explicit_overwrite_replaces_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "output.txt"
            output.write_text("original", encoding="utf-8")
            atomic_write_text(output, "replacement", overwrite=True)
            self.assertEqual(output.read_text(encoding="utf-8"), "replacement")


if __name__ == "__main__":
    unittest.main()
