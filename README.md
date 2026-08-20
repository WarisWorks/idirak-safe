# Idirak Safe

Idirak Safe is an experimental, local-first, open-source Uyghur transcription tool for people who may eventually need to handle sensitive human-rights documentation. The intended users include Uyghur-speaking advocates, journalists, researchers, archivists, and civil-society groups that want transcription to run on a device they control instead of uploading audio to a hosted service.

> [!WARNING]
> **Version 0.2.0a0 is pre-alpha and is not approved for sensitive use.** It now has an experimental CPU-only local ASR path, but its published accuracy has not yet been independently reproduced by this project. Use only synthetic, public, or explicitly consented non-sensitive test audio. Never treat its output as verified evidence.

Idirak Safe is a new, focused project. It is separate from the existing hosted services at [Idirak](https://www.idirak.com/); those services are not represented here as open-source, offline, or suitable for sensitive material.

## What is implemented

Version 0.2.0a0 provides:

- strict validation of local mono, 16 kHz, signed 16-bit PCM WAV input no longer than 30 seconds and no larger than 2 MiB;
- one explicitly selected, CPU-only `hf-wav2vec2` backend;
- support for exactly one model and revision: [`lucio/xls-r-uyghur-cv7`](https://huggingface.co/lucio/xls-r-uyghur-cv7) at `49339b194c6763d37414026456f7de09dd3f7554`;
- an embedded manifest that verifies the exact sizes and SHA-256 hashes of seven required model files before audio is opened;
- hard-offline model loading with local files, Safetensors, and remote code disabled;
- a single draft transcript segment covering the full input duration;
- deterministic local export to TXT, SRT, VTT, or normalized JSON;
- atomic output writes that preserve existing files unless `--force` is passed; and
- no telemetry, upload path, remote ASR API, or network fallback during transcription.

The following are not implemented:

- bundled model weights or an in-application model downloader;
- MP3, AAC, video, stereo, compressed WAV, resampling, or audio longer than 30 seconds;
- chunking, word-level timestamps, speaker labels, diarization, confidence scores, or human verification;
- a graphical interface, encrypted storage, secure deletion, or device protection; and
- evidence that the current model is reliable on diaspora speech, field recordings, code-switching, poor audio, or consequential human-rights material.

See the [architecture](docs/ARCHITECTURE.md), [model card](docs/MODEL_CARD.md), [data card](docs/DATA_CARD.md), and [roadmap](ROADMAP.md) for the exact scope and remaining work.

## Privacy principles

- **Local transcription:** after explicit setup, audio and transcript content are processed locally.
- **No silent network fallback:** a missing or invalid local component causes a clear failure.
- **No transcription-time download:** `transcribe` accepts a local model directory and never fetches a model.
- **No telemetry:** the command-line application does not send analytics, crash reports, audio, or transcript content.
- **Minimal output:** the ASR result omits the source filename and is written only to the path selected by the user.
- **Honest limitations:** a fluent-looking transcript can still contain dangerous errors and always requires comparison with the audio.

Local processing reduces exposure to a remote service, but it does not make a device safe. Idirak Safe does not provide disk encryption, anonymity, endpoint protection, malware protection, secure deletion guarantees, or legal advice.

## Install

Requirements:

- Python 3.10 or newer;
- Git; and
- enough local memory and storage for PyTorch, Transformers, and a 1,261,963,232-byte model weight file. Only one local smoke measurement exists; supported CPU speed and peak-memory requirements have not yet been benchmarked.

Clone and create a virtual environment:

```bash
git clone https://github.com/WarisWorks/idirak-safe.git
cd idirak-safe
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

For transcript validation and export only:

```bash
python -m pip install -e .
```

For the experimental local ASR backend:

```bash
python -m pip install -e '.[asr]'
```

On Windows PowerShell, activate the environment with `.venv\Scripts\Activate.ps1` instead.

Check the installed status:

```bash
idirak-safe doctor
```

## Explicit model setup

Model acquisition is a separate, networked setup action. It can reveal the model request to the network, Hugging Face, and local system logs or caches. Idirak Safe itself does not perform this download.

The following command pins the full revision and requests only the seven files in the built-in manifest:

```bash
mkdir -p models/lucio-xls-r-uyghur-cv7

DO_NOT_TRACK=1 HF_HUB_DISABLE_TELEMETRY=1 hf download lucio/xls-r-uyghur-cv7 \
  added_tokens.json \
  config.json \
  model.safetensors \
  preprocessor_config.json \
  special_tokens_map.json \
  tokenizer_config.json \
  vocab.json \
  --revision 49339b194c6763d37414026456f7de09dd3f7554 \
  --local-dir models/lucio-xls-r-uyghur-cv7
```

The `hf` command is provided by the `huggingface_hub` package installed with the ASR dependencies. Hugging Face may create a `.cache/huggingface` metadata directory inside `--local-dir`; that directory is not one of the seven model artifacts and is not needed for offline inference.

Verify the downloaded files before using audio:

```bash
idirak-safe verify-model \
  --model-dir models/lucio-xls-r-uyghur-cv7
```

`verify-model` checks the exact file sizes and SHA-256 hashes recorded in the packaged [manifest](src/idirak_safe/model_manifests/lucio-xls-r-uyghur-cv7.json). The weight file must be exactly 1,261,963,232 bytes with SHA-256 `aa923e217495329501fbea56cd3a8f695521a726525cb0c37ca143b1c262e2c6`. Verification establishes byte identity with the pinned artifacts; it does not establish accuracy, safety, consent, or legal suitability.

## Transcribe a non-sensitive test file

Input must be a regular, non-symlinked WAV file containing uncompressed mono audio at exactly 16,000 Hz with signed 16-bit samples. It must be at most 30 seconds and 2 MiB. Idirak Safe does not convert unsupported media.

```bash
idirak-safe transcribe sample.wav \
  --backend hf-wav2vec2 \
  --model-dir models/lucio-xls-r-uyghur-cv7 \
  --format json \
  --output sample.transcript.json
```

Supported output formats are `txt`, `srt`, `vtt`, and `json`. The current backend produces one segment from `0.0` to the audio duration; it does not produce word-level or sentence-level timing. Existing outputs are not replaced unless `--force` is supplied, and the output path may not be the audio input path.

At transcription time, the backend sets Hugging Face and Transformers offline flags before importing those libraries, loads only from `--model-dir` with `local_files_only=True`, refuses remote model code, requires Safetensors, and moves the model to CPU. It does not download weights or call a remote API.

### Model output and published evidence

The backend performs greedy CTC decoding: it runs the local Wav2Vec2 model, selects the highest-logit token at each step, and decodes the result with the local processor. It uses no language prompt. The model vocabulary is Uyghur Perso-Arabic script.

In one local smoke test on an 8 GB Apple Silicon Mac, a public CC0 Common Voice v24 Uyghur sample lasting 6.552 seconds produced Arabic-script output in 7.02 seconds. `/usr/bin/time` reported maximum resident memory of 1,452,851,200 bytes, approximately 1.35 GiB. The same output was reproduced with all network access denied by a macOS `sandbox-exec` profile. This is one functional observation, not an accuracy benchmark, supported-device guarantee, or security audit; the sample and output remain ignored and must not be committed.

The publisher states that punctuation was removed from the model vocabulary and describes the model as suitable only for low-fidelity uses such as draft video captions or indexing recorded broadcasts—not reliable live captions. The publisher reports WER `25.845%` and CER `4.795%` on Common Voice 7. These figures are self-reported in the upstream [model card](https://huggingface.co/lucio/xls-r-uyghur-cv7) and have not yet been independently reproduced by Idirak Safe.

## Export an existing transcript

The CLI also accepts a local JSON transcript with a required, non-empty `segments` list. `language` defaults to `ug`; `source` and segment-level `speaker` values are optional.

```json
{
  "language": "ug",
  "source": "interview-01.wav",
  "segments": [
    {
      "start": 0.0,
      "end": 2.4,
      "text": "سالام دۇنيا"
    }
  ]
}
```

Export it locally:

```bash
idirak-safe export examples/sample_transcript.json \
  --format txt \
  --output transcript.txt
```

This conversion validates and reformats existing text; it does not perform speech recognition.

## Run tests

```bash
python -m unittest discover -s tests -v
```

The unit tests exercise input constraints, manifest verification, offline loader options, greedy CTC decoding, transcript validation, failure behavior, and exporters. They do not independently measure ASR accuracy or constitute a security audit.

## Safe-use limitations

- Do not use version 0.2.0a0 with testimony, operational recordings, or identifiable information about at-risk people.
- Treat every generated transcript as an unverified draft and review it against the original audio. Errors can change names, dates, numbers, quotations, negation, and meaning.
- The current model has not been evaluated here for dialects, diaspora varieties, code-switching, emotional speech, overlapping speakers, compression, or field noise.
- A verified model hash does not show that the model is unbiased, accurate, ethically sourced, or safe.
- Protect the device, model directory, audio, output, backups, swap, shell history, and cloud-synced folders according to the user's risk environment.
- Consider whether possessing the audio or transcript could endanger someone before creating either one.

Security and privacy concerns can be reported using [SECURITY.md](SECURITY.md). Do not include sensitive recordings, transcripts, identities, credentials, or vulnerability details in a public issue.

## Project links

- Repository: <https://github.com/WarisWorks/idirak-safe>
- Idirak: <https://www.idirak.com/>
- Developer portfolio: <https://warisruzi.com/>
- Developer profiles: <https://github.com/WarisWorks> and <https://github.com/WarisRuzi>

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request. Do not submit private recordings, personal data, confidential testimony, unlicensed datasets, or model files whose provenance is unclear.

## Licences

- Idirak Safe source code: [Apache License 2.0](LICENSE).
- Selected fine-tuned model: its Hugging Face metadata declares [Apache-2.0](https://huggingface.co/lucio/xls-r-uyghur-cv7).
- `facebook/wav2vec2-xls-r-300m` base checkpoint: its Hugging Face metadata declares [Apache-2.0](https://huggingface.co/facebook/wav2vec2-xls-r-300m).
- Mozilla Common Voice 7 Uyghur data named by the model publisher: Common Voice datasets are released under [CC0 unless otherwise specified](https://commonvoice.mozilla.org/terms).
- Hugging Face Transformers runtime: [Apache License 2.0](https://github.com/huggingface/transformers/blob/main/LICENSE).

The selected model repository declares its licence in model-card metadata but does not contain a standalone licence file in the pinned file set. This project does not redistribute the weights, and the complete third-party dependency and redistribution review remains a release gate. See the [model card](docs/MODEL_CARD.md) and [data card](docs/DATA_CARD.md).
