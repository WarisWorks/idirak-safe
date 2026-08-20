from pathlib import Path
import tempfile
import unittest
import wave

from idirak_safe.audio import AudioValidationError, read_pcm16_wav


def write_wav(
    path: Path,
    *,
    channels: int = 1,
    sample_width: int = 2,
    sample_rate: int = 16_000,
    frames: int = 160,
) -> None:
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(sample_width)
        wav.setframerate(sample_rate)
        wav.writeframes(b"\0" * frames * channels * sample_width)


class AudioTests(unittest.TestCase):
    def test_reads_strict_pcm_wav(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.wav"
            write_wav(path)

            audio = read_pcm16_wav(path)

            self.assertEqual(audio.sample_rate, 16_000)
            self.assertEqual(audio.frame_count, 160)
            self.assertAlmostEqual(audio.duration, 0.01)

    def test_rejects_stereo(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.wav"
            write_wav(path, channels=2)
            with self.assertRaisesRegex(AudioValidationError, "mono"):
                read_pcm16_wav(path)

    def test_rejects_wrong_sample_rate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.wav"
            write_wav(path, sample_rate=8_000)
            with self.assertRaisesRegex(AudioValidationError, "16000"):
                read_pcm16_wav(path)

    def test_rejects_wrong_sample_width(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.wav"
            write_wav(path, sample_width=1)
            with self.assertRaisesRegex(AudioValidationError, "16-bit"):
                read_pcm16_wav(path)

    def test_rejects_audio_over_thirty_seconds(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.wav"
            write_wav(path, frames=16_000 * 31)
            with self.assertRaisesRegex(AudioValidationError, "30-second"):
                read_pcm16_wav(path)

    def test_rejects_truncated_wav(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.wav"
            path.write_bytes(b"RIFF\0\0")
            with self.assertRaisesRegex(AudioValidationError, "valid PCM WAV"):
                read_pcm16_wav(path)

    def test_rejects_symbolic_link(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "sample.wav"
            link = Path(directory) / "linked.wav"
            write_wav(target)
            link.symlink_to(target)
            with self.assertRaisesRegex(AudioValidationError, "symbolic link"):
                read_pcm16_wav(link)


if __name__ == "__main__":
    unittest.main()
