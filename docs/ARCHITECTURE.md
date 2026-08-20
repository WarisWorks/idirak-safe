# Architecture

## Document status

This document describes the implementation in Idirak Safe `0.2.0a0`. The release contains an experimental local Wav2Vec2/XLS-R CTC path, not merely an interface scaffold. The path is intentionally narrow and is **not approved for sensitive use**.

## Security objective

Idirak Safe is intended to create and export a Uyghur draft transcript on a device controlled by the user without sending audio or transcript content to a hosted service. The core invariant is:

> A missing, changed, broken, or unsupported local component causes an explicit failure. It never triggers a remote API or silent network fallback.

Local execution narrows the data path. It does not secure a compromised device, encrypt a disk, anonymize a user, guarantee secure deletion, prove model provenance, or make an inaccurate transcript trustworthy.

## Two separate workflows

Model acquisition and transcription are deliberately separate.

### Explicit setup workflow

```text
User invokes external `hf download`
              |
              v
Hugging Face model repository
lucio/xls-r-uyghur-cv7
exact revision 49339b194c6763d37414026456f7de09dd3f7554
              |
              v
Seven requested files in a user-selected local model directory
              |
              v
`idirak-safe verify-model --model-dir ...`
size + SHA-256 verification against the packaged manifest
```

This is a user-initiated network event outside the Idirak Safe transcription command. The request can be visible to the network, Hugging Face, shell history, and local cache metadata. The model weights are not bundled with this repository or Python package.

The built-in manifest supports only [`lucio/xls-r-uyghur-cv7`](https://huggingface.co/lucio/xls-r-uyghur-cv7) at the full revision above. It lists these seven files:

1. `added_tokens.json`
2. `config.json`
3. `model.safetensors`
4. `preprocessor_config.json`
5. `special_tokens_map.json`
6. `tokenizer_config.json`
7. `vocab.json`

The weight file is exactly 1,261,963,232 bytes with SHA-256 `aa923e217495329501fbea56cd3a8f695521a726525cb0c37ca143b1c262e2c6`. The packaged [manifest](../src/idirak_safe/model_manifests/lucio-xls-r-uyghur-cv7.json) records the sizes and SHA-256 hashes for all seven files.

The verifier requires every listed file to be a regular file with the expected byte size and digest. The model directory itself may not be a symbolic link; top-level symbolic links and files with executable, library, Python, pickle, PyTorch-pickle, or similar unsafe suffixes are rejected.

Verification proves only that the required local bytes match the packaged manifest. It does not prove accuracy, absence of malicious learned behavior, ethical data collection, licence sufficiency, or safety. Extra non-symlink directories and file types not on the unsafe list are not a complete sandbox and remain part of the local trust boundary.

### Offline transcription workflow

```text
CLI arguments
    |
    +--> reject identical audio/output paths
    |
    +--> verify local model before opening audio
              |
              v
regular, non-symlinked local WAV
              |
              v
strict WAV validation
mono | 16,000 Hz | signed PCM16 | <= 30 s | <= 2 MiB
              |
              v
PCM samples normalized in memory
              |
              v
CPU-only Hugging Face Wav2Vec2 CTC adapter
local files only | Safetensors | remote code disabled
              |
              v
model logits -> argmax -> local CTC processor decode
              |
              v
one in-memory `ug` draft transcript segment
0.0 seconds -> full audio duration
              |
              v
TXT / SRT / VTT / JSON renderer
              |
              v
atomic write to the user-selected local output path
```

No URL input, cloud storage discovery, server-side processing, hosted inference, or remote fallback exists in this path.

## Components

### CLI boundary

The `transcribe` command requires all consequential choices to be explicit:

- local audio path;
- `--backend hf-wav2vec2`;
- local `--model-dir`;
- output format; and
- local output path.

Only `hf-wav2vec2` is allowlisted. Dynamic plugins and arbitrary backend identifiers are not supported. The audio and output paths must differ even when `--force` is supplied.

### Model verifier

`HFWav2Vec2Backend` verifies the selected model directory during construction, before the audio file is opened. The embedded manifest records:

- model ID;
- immutable revision;
- declared model and training-data licences;
- exact required filenames and byte sizes; and
- SHA-256 for every required file.

The runtime never loads the upstream `pytorch_model.bin`, `training_args.bin`, `eval.py`, or another Python or pickle-based artifact. `model.safetensors` is the only model weight artifact in the manifest.

### Audio boundary

The importer uses Python's standard-library WAV reader. It accepts only a regular, non-symlinked file that is:

- uncompressed WAV;
- one channel;
- exactly 16,000 Hz;
- signed 16-bit PCM;
- non-empty;
- at most 480,000 frames, or 30 seconds; and
- at most 2 MiB on disk.

It opens the path with `O_NOFOLLOW` where the operating system provides that flag, checks the opened file descriptor again, and rejects truncated PCM data. It performs no codec decoding, resampling, metadata extraction, or temporary-file conversion.

### Offline ASR adapter

Before importing Hugging Face libraries, the adapter sets:

```text
DO_NOT_TRACK=1
HF_DATASETS_OFFLINE=1
HF_HUB_DISABLE_PROGRESS_BARS=1
HF_HUB_DISABLE_TELEMETRY=1
HF_HUB_OFFLINE=1
TRANSFORMERS_OFFLINE=1
```

If `huggingface_hub` or `transformers` was already imported in the process without `HF_HUB_OFFLINE=1`, the backend refuses to continue and asks for a fresh process. The processor and model are loaded from the verified local directory with `local_files_only=True` and `trust_remote_code=False`; the model additionally requires `use_safetensors=True`. The model is moved to CPU and inference runs under PyTorch inference mode.

The adapter sends the normalized sample array to `AutoModelForCTC`, selects the highest-logit token at every time step with `torch.argmax`, and decodes the token IDs with the local processor. There is no language prompt, external language model, remote decoder, or punctuation restoration stage.

These controls mean the supported transcription path does not download a model or call a remote inference API. They are not a general operating-system network sandbox.

### Canonical transcript and exporters

The ASR adapter returns one `Transcript` object in memory:

```json
{
  "language": "ug",
  "segments": [
    {
      "start": 0.0,
      "end": 12.3,
      "text": "generated draft text"
    }
  ]
}
```

The generated transcript intentionally omits `source`, so the input filename is not copied into the output. The current CTC call does not return word, sentence, confidence, or speaker metadata. The one segment spans the entire validated audio duration.

Exporters render TXT, SRT, VTT, or normalized UTF-8 JSON. They do not correct recognition errors, restore punctuation, or mark a transcript as human-reviewed. The output is written through a same-directory temporary file and an atomic link or replacement. New files use private temporary-file permissions. Existing output is preserved unless the user explicitly supplies `--force`.

If validation, dependency loading, model loading, inference, decoding, transcript validation, rendering, or writing fails, the command exits non-zero. It does not report success or intentionally leave a partial transcript at the requested output path.

## Network policy

The runtime design prohibits:

- model download from `verify-model`, `transcribe`, or `export`;
- automatic fallback from local inference to a hosted service;
- upload of audio, transcript text, prompts, filenames, analytics, or crash reports;
- arbitrary remote model code; and
- remote authentication or licence checks required to transcribe.

Package installation and the documented external `hf download` command may use the network. They must happen as explicit setup actions and should be performed with awareness that obtaining the software or model can itself be observable.

## Current smoke-test evidence

The exact pinned model passed the packaged size and SHA-256 verification. On an 8 GB Apple Silicon Mac, a public CC0 Common Voice v24 Uyghur sample of 6.552 seconds:

- produced Arabic-script Uyghur output;
- completed in 7.02 seconds;
- reached a maximum resident set size of 1,452,851,200 bytes, approximately 1.35 GiB as reported by `/usr/bin/time`; and
- reproduced the same output when run under a macOS `sandbox-exec` profile denying all network access.

This is one functional smoke test, not an accuracy benchmark, portability result, security audit, or claim about the Common Voice 7 test score. The sample and generated output remain local and ignored; they must not be committed.

## Data lifecycle

```text
Original WAV        remains at the user-selected path; never modified
Decoded PCM         held in process memory for the run
Model               remains in the user-selected local directory
Transcript state    held in memory until an explicit output write
Output              written to the user-selected path
Temporary output    same directory; removed after success or handled failure
Application logs    status/error text; no audio or transcript content by design
Telemetry           none
```

The application does not delete the original audio, model, or output. Process memory, operating-system caches, swap, backups, filesystem snapshots, indexing, crash systems, and cloud-synced folders can create or retain additional copies. Idirak Safe cannot promise secure deletion.

## Trust boundaries

- **Trusted for a run:** the device, operating system, Python environment, installed Idirak Safe code, PyTorch/Transformers stack, verified model bytes, and chosen output directory.
- **Untrusted input:** WAV contents and structure, transcript JSON supplied to `export`, filenames, model directory contents before verification, and all third-party artifacts before review.
- **Explicit external setup:** Git, Python package indexes, and Hugging Face are outside the offline transcription boundary.
- **Human review:** generated text remains unverified, especially for names, numbers, dates, negation, dialectal speech, and consequential statements.

See the [threat model](../THREAT_MODEL.md), [privacy document](../PRIVACY.md), [model card](MODEL_CARD.md), and [data card](DATA_CARD.md).

## Remaining verification work

- Independently reproduce or refute the publisher's Common Voice 7 WER and CER under the exact pinned revision and documented decoding.
- Evaluate on licensed, non-sensitive speech beyond the upstream test setting, including diaspora varieties, noise, code-switching, names, dates, numbers, and negation.
- Repeat performance and memory measurements on documented CPU-only reference systems.
- Convert the one-off network-denied smoke test into automated, repeatable regression coverage and test additional supported environments.
- Inspect temporary files, logs, process environment, caches, and crash behavior.
- Complete dependency, model, data, and redistribution review.
- Obtain an independent privacy/security review before considering any sensitive pilot.

Until those checks are completed and published, Idirak Safe remains pre-alpha and unsuitable for sensitive material.
