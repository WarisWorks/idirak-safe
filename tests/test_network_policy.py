"""Regression guards for the no-network policy.

These checks run inside the Python process. They complement, and do not
replace, running the tool with networking denied by the operating system.
"""

import ast
from contextlib import redirect_stderr, redirect_stdout
import hashlib
from io import StringIO
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

import idirak_safe
from idirak_safe.cli import main
from idirak_safe.model_files import ManifestFile, ModelManifest


PACKAGE_ROOT = Path(idirak_safe.__file__).resolve().parent

# Standard-library and third-party modules that open network connections,
# start other programs, or load arbitrary code. The optional ASR stack is
# imported only by ``hf_wav2vec2`` after its offline flags are forced.
FORBIDDEN_MODULES = {
    "aiohttp",
    "asyncio",
    "ftplib",
    "http",
    "httpx",
    "huggingface_hub",
    "imaplib",
    "multiprocessing",
    "pickle",
    "poplib",
    "requests",
    "smtplib",
    "socket",
    "socketserver",
    "ssl",
    "subprocess",
    "telnetlib",
    "urllib",
    "urllib3",
    "webbrowser",
    "xmlrpc",
}
ASR_ONLY_MODULES = {"numpy", "safetensors", "torch", "transformers"}


def _imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            modules.add(node.module.split(".")[0])
    return modules


class NetworkPolicyTests(unittest.TestCase):
    def test_source_imports_no_network_or_process_modules(self) -> None:
        sources = sorted(PACKAGE_ROOT.rglob("*.py"))
        self.assertTrue(sources)
        for source in sources:
            with self.subTest(source=source.name):
                self.assertEqual(_imported_modules(source) & FORBIDDEN_MODULES, set())

    def test_asr_libraries_are_confined_to_the_backend_adapter(self) -> None:
        for source in sorted(PACKAGE_ROOT.rglob("*.py")):
            if source.name == "hf_wav2vec2.py":
                continue
            with self.subTest(source=source.name):
                self.assertEqual(_imported_modules(source) & ASR_ONLY_MODULES, set())

    def test_export_and_verify_run_with_sockets_denied(self) -> None:
        def deny(*args: object, **kwargs: object) -> None:
            raise AssertionError("network access attempted")

        content = b"safe model fixture"
        manifest = ModelManifest(
            model_id="example/model",
            revision="a" * 40,
            model_license="Apache-2.0",
            training_data="synthetic",
            training_data_license="CC0-1.0",
            files=(
                ManifestFile(
                    path="model.safetensors",
                    size=len(content),
                    sha256=hashlib.sha256(content).hexdigest(),
                ),
            ),
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            model_dir = root / "model"
            model_dir.mkdir()
            (model_dir / "model.safetensors").write_bytes(content)
            transcript = root / "input.json"
            transcript.write_text(
                '{"segments": [{"start": 0, "end": 1, "text": "سالام"}]}',
                encoding="utf-8",
            )
            with (
                patch.object(socket, "socket", deny),
                patch.object(socket, "create_connection", deny),
                patch.object(socket, "getaddrinfo", deny),
                patch("idirak_safe.model_files.load_manifest", return_value=manifest),
                redirect_stdout(StringIO()),
                redirect_stderr(StringIO()),
            ):
                self.assertEqual(main(["doctor"]), 0)
                self.assertEqual(
                    main(["verify-model", "--model-dir", str(model_dir)]), 0
                )
                for output_format in ("txt", "srt", "vtt", "json"):
                    status = main(
                        [
                            "export",
                            str(transcript),
                            "--format",
                            output_format,
                            "--output",
                            str(root / f"output.{output_format}"),
                        ]
                    )
                    self.assertEqual(status, 0)


if __name__ == "__main__":
    unittest.main()
