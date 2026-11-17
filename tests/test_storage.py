import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

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

    def test_overwrite_and_default_leave_no_temporary_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "output.txt"
            atomic_write_text(output, "first")
            atomic_write_text(output, "second", overwrite=True)
            with self.assertRaises(FileExistsError):
                atomic_write_text(output, "third")
            self.assertEqual([item.name for item in Path(directory).iterdir()], ["output.txt"])

    def test_falls_back_when_hard_links_are_unsupported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "output.txt"
            with patch("idirak_safe.storage.os.link", side_effect=PermissionError):
                atomic_write_text(output, "ئۇيغۇرچە\n")
                self.assertEqual(output.read_text(encoding="utf-8"), "ئۇيغۇرچە\n")
                with self.assertRaisesRegex(FileExistsError, "--force"):
                    atomic_write_text(output, "replacement")
            self.assertEqual(output.read_text(encoding="utf-8"), "ئۇيغۇرچە\n")
            self.assertEqual([item.name for item in Path(directory).iterdir()], ["output.txt"])

    def test_failed_fallback_removes_only_its_reservation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "output.txt"
            with (
                patch("idirak_safe.storage.os.link", side_effect=PermissionError),
                patch("idirak_safe.storage.os.replace", side_effect=OSError("disk")),
                self.assertRaisesRegex(OSError, "disk"),
            ):
                atomic_write_text(output, "content")
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_rejects_directory_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(IsADirectoryError):
                atomic_write_text(directory, "content", overwrite=True)

    @unittest.skipUnless(os.name == "posix", "POSIX permission bits are required")
    def test_new_output_is_private(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "output.txt"
            atomic_write_text(output, "content")
            self.assertEqual(output.stat().st_mode & 0o077, 0)


if __name__ == "__main__":
    unittest.main()
