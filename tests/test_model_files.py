import hashlib
import os
from pathlib import Path
import tempfile
import unittest

from idirak_safe.model_files import (
    ManifestFile,
    ModelManifest,
    ModelVerificationError,
    load_manifest,
    verify_model_directory,
)


def manifest_for(name: str, content: bytes) -> ModelManifest:
    return ModelManifest(
        model_id="example/model",
        revision="a" * 40,
        model_license="Apache-2.0",
        training_data="synthetic",
        training_data_license="CC0-1.0",
        files=(
            ManifestFile(
                path=name,
                size=len(content),
                sha256=hashlib.sha256(content).hexdigest(),
            ),
        ),
    )


class ModelFileTests(unittest.TestCase):
    def test_builtin_manifest_is_pinned(self) -> None:
        manifest = load_manifest()
        self.assertEqual(
            manifest.revision, "49339b194c6763d37414026456f7de09dd3f7554"
        )
        self.assertIn("model.safetensors", {item.path for item in manifest.files})
        self.assertNotIn("training_args.bin", {item.path for item in manifest.files})

    def test_verifies_regular_file_hash(self) -> None:
        content = b"safe model fixture"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "model.safetensors"
            path.write_bytes(content)
            result = verify_model_directory(
                directory, manifest=manifest_for(path.name, content)
            )
            self.assertEqual(result.model_id, "example/model")

    def test_rejects_hash_mismatch(self) -> None:
        expected = b"expected"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "model.safetensors"
            path.write_bytes(b"tampered")
            with self.assertRaisesRegex(ModelVerificationError, "wrong size|SHA-256"):
                verify_model_directory(
                    directory, manifest=manifest_for(path.name, expected)
                )

    def test_rejects_pickle_weight(self) -> None:
        content = b"unsafe"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "training_args.bin"
            path.write_bytes(content)
            with self.assertRaisesRegex(ModelVerificationError, "unsafe file type"):
                verify_model_directory(
                    directory, manifest=manifest_for("safe.json", b"missing")
                )

    @unittest.skipUnless(os.name == "posix", "POSIX executable bits are required")
    def test_rejects_executable_file(self) -> None:
        content = b"safe model fixture"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            model = root / "model.safetensors"
            executable = root / "unexpected-tool"
            model.write_bytes(content)
            executable.write_text("#!/bin/sh\n", encoding="utf-8")
            executable.chmod(0o755)
            with self.assertRaisesRegex(ModelVerificationError, "executable file"):
                verify_model_directory(
                    root, manifest=manifest_for(model.name, content)
                )

    def test_rejects_unverified_processor_configuration(self) -> None:
        content = b"safe model fixture"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            model = root / "model.safetensors"
            model.write_bytes(content)
            (root / "processor_config.json").write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ModelVerificationError, "unexpected entry"):
                verify_model_directory(
                    root, manifest=manifest_for(model.name, content)
                )

    def test_rejects_symlinked_model_file(self) -> None:
        content = b"model"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target.safetensors"
            link = root / "model.safetensors"
            target.write_bytes(content)
            link.symlink_to(target)
            with self.assertRaisesRegex(ModelVerificationError, "symbolic link"):
                verify_model_directory(
                    root, manifest=manifest_for(link.name, content)
                )


if __name__ == "__main__":
    unittest.main()
