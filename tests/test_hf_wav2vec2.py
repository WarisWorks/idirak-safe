from contextlib import nullcontext
import os
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest
from unittest.mock import MagicMock, patch

from idirak_safe.asr import BackendExecutionError, BackendUnavailableError
from idirak_safe.audio import PCM16Audio
from idirak_safe.hf_wav2vec2 import (
    HFWav2Vec2Backend,
    _OFFLINE_ENVIRONMENT,
    _load_dependencies,
)


class FakeNumpy:
    float32 = "float32"

    @staticmethod
    def frombuffer(value: bytes, dtype: str) -> MagicMock:
        result = MagicMock()
        result.astype.return_value.__truediv__.return_value = "samples"
        return result


class FakeProcessor:
    def __call__(self, samples: object, **kwargs: object) -> SimpleNamespace:
        return SimpleNamespace(input_values="features")

    def batch_decode(self, ids: object) -> list[str]:
        return ["ياخشىمۇسىز"]


class HFWav2Vec2Tests(unittest.TestCase):
    def _backend(self) -> HFWav2Vec2Backend:
        with patch("idirak_safe.hf_wav2vec2.verify_model_directory"):
            return HFWav2Vec2Backend(model_dir=Path("/local/model"))

    def test_uses_local_only_safetensors_loading(self) -> None:
        processor_factory = MagicMock()
        processor_factory.from_pretrained.return_value = FakeProcessor()
        model = MagicMock()
        model.return_value = SimpleNamespace(logits="logits")
        model_factory = MagicMock()
        model_factory.from_pretrained.return_value = model
        fake_torch = SimpleNamespace(
            inference_mode=lambda: nullcontext(),
            argmax=MagicMock(return_value="ids"),
        )
        audio = PCM16Audio(pcm=b"\0\0" * 160, sample_rate=16_000, frame_count=160)

        with (
            patch("idirak_safe.hf_wav2vec2.read_pcm16_wav", return_value=audio),
            patch(
                "idirak_safe.hf_wav2vec2._load_dependencies",
                return_value=(FakeNumpy, fake_torch, processor_factory, model_factory),
            ),
        ):
            transcript = self._backend().transcribe(Path("sample.wav"))

        processor_factory.from_pretrained.assert_called_once_with(
            "/local/model", local_files_only=True, trust_remote_code=False
        )
        model_factory.from_pretrained.assert_called_once_with(
            "/local/model",
            local_files_only=True,
            trust_remote_code=False,
            use_safetensors=True,
        )
        model.assert_called_once_with(input_values="features")
        fake_torch.argmax.assert_called_once_with("logits", dim=-1)
        self.assertEqual(transcript.segments[0].text, "ياخشىمۇسىز")
        self.assertIsNone(transcript.source)

    def test_empty_output_fails_without_transcript(self) -> None:
        processor = FakeProcessor()
        processor.batch_decode = MagicMock(return_value=["   "])
        processor_factory = MagicMock()
        processor_factory.from_pretrained.return_value = processor
        model = MagicMock(return_value=SimpleNamespace(logits="logits"))
        model_factory = MagicMock()
        model_factory.from_pretrained.return_value = model
        fake_torch = SimpleNamespace(
            inference_mode=lambda: nullcontext(),
            argmax=MagicMock(return_value="ids"),
        )
        audio = PCM16Audio(pcm=b"\0\0" * 160, sample_rate=16_000, frame_count=160)

        with (
            patch("idirak_safe.hf_wav2vec2.read_pcm16_wav", return_value=audio),
            patch(
                "idirak_safe.hf_wav2vec2._load_dependencies",
                return_value=(FakeNumpy, fake_torch, processor_factory, model_factory),
            ),
        ):
            with self.assertRaisesRegex(BackendExecutionError, "produced no text"):
                self._backend().transcribe(Path("sample.wav"))

    def test_verifies_model_before_opening_audio(self) -> None:
        with (
            patch(
                "idirak_safe.hf_wav2vec2.verify_model_directory",
                side_effect=RuntimeError("unverified"),
            ),
            patch("idirak_safe.hf_wav2vec2.read_pcm16_wav") as read_audio,
        ):
            with self.assertRaisesRegex(RuntimeError, "unverified"):
                HFWav2Vec2Backend(model_dir=Path("/local/model"))
        read_audio.assert_not_called()

    def test_fails_if_hub_was_imported_before_offline_mode(self) -> None:
        loaded_hub = SimpleNamespace(is_offline_mode=lambda: False)
        with (
            patch.dict(os.environ, {}, clear=True),
            patch.dict(
                sys.modules,
                {"huggingface_hub": loaded_hub, "transformers": None},
            ),
        ):
            with self.assertRaisesRegex(
                BackendUnavailableError, "imported before verified offline mode"
            ):
                _load_dependencies()
            self.assertEqual(os.environ["HF_HUB_OFFLINE"], "1")
            self.assertEqual(os.environ["TRANSFORMERS_OFFLINE"], "1")
            self.assertEqual(os.environ["HF_HUB_DISABLE_TELEMETRY"], "1")

    def test_fails_when_environment_changes_after_online_hub_import(self) -> None:
        loaded_hub = SimpleNamespace(is_offline_mode=lambda: False)
        with (
            patch.dict(os.environ, _OFFLINE_ENVIRONMENT, clear=True),
            patch.dict(
                sys.modules,
                {"huggingface_hub": loaded_hub, "transformers": None},
            ),
        ):
            with self.assertRaisesRegex(
                BackendUnavailableError, "imported before verified offline mode"
            ):
                _load_dependencies()


if __name__ == "__main__":
    unittest.main()
