"""Explicit allowlist boundary for experimental local ASR backends."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from .model import Transcript


class ASRError(RuntimeError):
    """Base class for expected local transcription failures."""


class BackendUnavailableError(ASRError):
    """Raised when optional local inference dependencies are unavailable."""


class BackendExecutionError(ASRError):
    """Raised when local inference cannot produce a safe result."""


class ASRBackend(Protocol):
    backend_id: str

    def transcribe(self, audio_path: Path) -> Transcript:
        """Transcribe one validated local audio file."""


def create_backend(name: str, *, model_dir: Path) -> ASRBackend:
    """Create one hard-coded backend; dynamic plugins are deliberately unsupported."""

    if name != "hf-wav2vec2":
        raise BackendUnavailableError(f"unsupported ASR backend: {name}")

    from .hf_wav2vec2 import HFWav2Vec2Backend

    return HFWav2Vec2Backend(model_dir=model_dir)
