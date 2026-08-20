"""Strict, bounded PCM-WAV input for the experimental local ASR backend."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import stat
import wave


EXPECTED_SAMPLE_RATE = 16_000
MAX_DURATION_SECONDS = 30.0
MAX_FILE_BYTES = 2 * 1024 * 1024


class AudioValidationError(RuntimeError):
    """Raised when audio is outside the intentionally narrow MVP format."""


@dataclass(frozen=True, slots=True)
class PCM16Audio:
    pcm: bytes
    sample_rate: int
    frame_count: int

    @property
    def duration(self) -> float:
        return self.frame_count / self.sample_rate


def read_pcm16_wav(path: str | Path) -> PCM16Audio:
    """Read at most 30 seconds of mono, 16 kHz, signed 16-bit PCM WAV."""

    audio_path = Path(path)
    if audio_path.is_symlink():
        raise AudioValidationError("audio input must not be a symbolic link")

    try:
        metadata = audio_path.stat()
    except OSError as error:
        raise AudioValidationError("audio input cannot be opened") from error
    if not stat.S_ISREG(metadata.st_mode):
        raise AudioValidationError("audio input must be a regular file")
    if metadata.st_size == 0:
        raise AudioValidationError("audio input is empty")
    if metadata.st_size > MAX_FILE_BYTES:
        raise AudioValidationError("audio input exceeds the 2 MiB safety limit")

    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(audio_path, flags)
    except OSError as error:
        raise AudioValidationError("audio input cannot be opened safely") from error

    try:
        opened_metadata = os.fstat(descriptor)
        if not stat.S_ISREG(opened_metadata.st_mode):
            raise AudioValidationError("audio input must be a regular file")
        if opened_metadata.st_size == 0:
            raise AudioValidationError("audio input is empty")
        if opened_metadata.st_size > MAX_FILE_BYTES:
            raise AudioValidationError("audio input exceeds the 2 MiB safety limit")
        with os.fdopen(descriptor, "rb", closefd=False) as raw_audio:
            try:
                with wave.open(raw_audio, "rb") as wav:
                    if wav.getcomptype() != "NONE":
                        raise AudioValidationError("audio must use uncompressed PCM")
                    if wav.getnchannels() != 1:
                        raise AudioValidationError("audio must be mono")
                    if wav.getsampwidth() != 2:
                        raise AudioValidationError("audio must use signed 16-bit samples")
                    if wav.getframerate() != EXPECTED_SAMPLE_RATE:
                        raise AudioValidationError("audio sample rate must be exactly 16000 Hz")

                    frame_count = wav.getnframes()
                    if frame_count <= 0:
                        raise AudioValidationError("audio contains no samples")
                    if frame_count > int(EXPECTED_SAMPLE_RATE * MAX_DURATION_SECONDS):
                        raise AudioValidationError("audio exceeds the 30-second MVP limit")
                    pcm = wav.readframes(frame_count)
            except (EOFError, wave.Error) as error:
                raise AudioValidationError("audio is not a valid PCM WAV file") from error
    finally:
        os.close(descriptor)

    if len(pcm) != frame_count * 2:
        raise AudioValidationError("audio data is truncated")
    return PCM16Audio(
        pcm=pcm,
        sample_rate=EXPECTED_SAMPLE_RATE,
        frame_count=frame_count,
    )
