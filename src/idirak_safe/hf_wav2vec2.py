"""Experimental, CPU-only, offline Hugging Face Wav2Vec2 CTC adapter."""

from __future__ import annotations

import os
from pathlib import Path
import sys
from typing import Any

from .asr import BackendExecutionError, BackendUnavailableError
from .audio import PCM16Audio, read_pcm16_wav
from .model import Segment, Transcript, TranscriptValidationError
from .model_files import ModelManifest, verify_model_directory


_OFFLINE_ENVIRONMENT = {
    "DO_NOT_TRACK": "1",
    "HF_DATASETS_OFFLINE": "1",
    "HF_HUB_DISABLE_PROGRESS_BARS": "1",
    "HF_HUB_DISABLE_TELEMETRY": "1",
    "HF_HUB_OFFLINE": "1",
    "TRANSFORMERS_OFFLINE": "1",
}


def _load_dependencies() -> tuple[Any, Any, Any, Any]:
    """Import optional dependencies only after forcing their offline flags."""

    loaded_hub = sys.modules.get("huggingface_hub")
    loaded_transformers = sys.modules.get("transformers")
    already_imported = loaded_hub is not None or loaded_transformers is not None
    was_fully_configured = all(
        os.environ.get(key) == value for key, value in _OFFLINE_ENVIRONMENT.items()
    )
    cached_offline = False
    if loaded_hub is not None:
        offline_check = getattr(loaded_hub, "is_offline_mode", None)
        try:
            cached_offline = callable(offline_check) and offline_check() is True
        except Exception:
            cached_offline = False

    for key, value in _OFFLINE_ENVIRONMENT.items():
        os.environ[key] = value
    if already_imported and not (was_fully_configured and cached_offline):
        raise BackendUnavailableError(
            "Hugging Face libraries were imported before verified offline mode; "
            "run idirak-safe in a fresh process"
        )

    try:
        import numpy
        import torch
        from transformers import AutoModelForCTC, AutoProcessor
        from transformers.utils import logging as transformers_logging
    except ImportError as error:
        raise BackendUnavailableError(
            "local ASR dependencies are missing; install with: pip install -e '.[asr]'"
        ) from error

    transformers_logging.set_verbosity_error()
    transformers_logging.disable_progress_bar()
    return numpy, torch, AutoProcessor, AutoModelForCTC


def _decode_audio(numpy: Any, audio: PCM16Audio) -> Any:
    samples = numpy.frombuffer(audio.pcm, dtype="<i2").astype(numpy.float32)
    return samples / 32768.0


class HFWav2Vec2Backend:
    """Pinned Wav2Vec2 CTC inference with no download or remote-code path."""

    backend_id = "hf-wav2vec2"

    def __init__(self, *, model_dir: Path) -> None:
        self.model_dir = Path(model_dir)
        self.manifest: ModelManifest = verify_model_directory(self.model_dir)

    def transcribe(self, audio_path: Path) -> Transcript:
        audio = read_pcm16_wav(audio_path)
        numpy, torch, processor_class, model_class = _load_dependencies()

        try:
            processor = processor_class.from_pretrained(
                str(self.model_dir),
                local_files_only=True,
                trust_remote_code=False,
            )
            model = model_class.from_pretrained(
                str(self.model_dir),
                local_files_only=True,
                trust_remote_code=False,
                use_safetensors=True,
            )
            model.to("cpu")
            model.eval()

            samples = _decode_audio(numpy, audio)
            inputs = processor(
                samples,
                sampling_rate=audio.sample_rate,
                return_tensors="pt",
            )
            with torch.inference_mode():
                logits = model(input_values=inputs.input_values).logits
            predicted_ids = torch.argmax(logits, dim=-1)
            text = processor.batch_decode(predicted_ids)[0].strip()
        except BackendUnavailableError:
            raise
        except Exception as error:
            raise BackendExecutionError(
                "local ASR failed; no transcript was written"
            ) from error

        if not text:
            raise BackendExecutionError(
                "local ASR produced no text; no transcript was written"
            )
        if len(text) > 100_000 or any(ord(character) < 32 for character in text):
            raise BackendExecutionError(
                "local ASR produced invalid text; no transcript was written"
            )

        try:
            return Transcript(
                language="ug",
                segments=(Segment(start=0.0, end=audio.duration, text=text),),
            )
        except TranscriptValidationError as error:
            raise BackendExecutionError(
                "local ASR produced an invalid transcript; no output was written"
            ) from error
