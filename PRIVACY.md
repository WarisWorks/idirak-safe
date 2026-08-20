# Privacy

## Status

Idirak Safe is a pre-alpha project with an experimental local ASR path. It is not ready for sensitive, confidential, safety-critical, or high-risk material. Use only synthetic, public-domain, or explicitly consented non-sensitive test recordings.

The controls below describe the current experimental implementation. They reduce specific risks, but they are not an independent audit or a guarantee that the application, its dependencies, the device, or the surrounding workflow is private.

## Current local-ASR controls

The experimental `hf-wav2vec2` path, using the pinned `lucio/xls-r-uyghur-cv7` Wav2Vec2/CTC model, currently enforces the following application-level controls:

- `transcribe` accepts one explicitly selected local backend and local model directory. It has no model-download, hosted-ASR, remote fallback, authentication, or telemetry path.
- Required model files are checked against a built-in manifest containing a pinned upstream revision, exact sizes, and SHA-256 hashes before the audio file is opened. Symbolic links and common executable or pickle-based model file types are rejected.
- Transformers is instructed to load only local files with `local_files_only=True` and `trust_remote_code=False`. Model weights are required to load through Safetensors with `use_safetensors=True`.
- Before Hugging Face and Transformers are imported, the adapter forces `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `HF_DATASETS_OFFLINE=1`, `HF_HUB_DISABLE_TELEMETRY=1`, and `DO_NOT_TRACK=1`. If relevant libraries were imported first without offline mode, the adapter fails instead of continuing.
- Audio input must be a regular, non-symbolic-link, uncompressed WAV file no larger than 2 MiB: mono, 16 kHz, signed 16-bit PCM, non-empty, and no longer than 30 seconds. Unsupported or truncated input is rejected.
- The experimental adapter reads decoded PCM into process memory and does not intentionally create a decoded-audio file. It writes a transcript only after successful inference and validation.
- Generated transcripts omit the source filename. The application prints only the output basename on success, although command-line arguments, shell history, process inspection, and operating-system activity can still expose paths.

These are code-level controls, not a built-in operating-system network sandbox. The CPU backend and its Python, PyTorch, Transformers, Hugging Face, NumPy, and Safetensors dependencies run in the same process as Idirak Safe. One local macOS smoke test completed with network access denied by `sandbox-exec`, but that run did not independently monitor attempted connections and is not a repeatable, cross-platform integration test. Process isolation has not been implemented or independently reviewed.

## Data handling

No production data collection system or hosted transcription service is part of this repository. The repository, tests, security reports, and development workflow must not contain or accept:

- recordings, transcripts, identities, or metadata from activists, witnesses, survivors, or other at-risk people;
- scraped private communications or material obtained through surveillance;
- data whose origin, licence, or consent cannot be demonstrated; or
- API keys, access tokens, device identifiers, or other secrets.

Examples and tests should use synthetic audio, public-domain material, or data supported by documented informed consent and an appropriate licence. See [docs/DATA_CARD.md](docs/DATA_CARD.md).

## Setup downloads and network visibility

The `transcribe` command does not download a model. Installing Python dependencies and obtaining the pinned model are separate setup actions. Any such download is observable to the network provider and hosting service and can reveal an IP address, time, package or model requested, and related metadata. A verified offline copy may reduce later network exposure, but it does not erase the original download record.

Offline environment variables and local-only loader options reduce accidental network use by the selected libraries, but they are not equivalent to a firewall or built-in OS-enforced network denial. A single successful macOS deny-network smoke test is encouraging, but until a repeatable test monitors connection attempts across supported platforms and an independent review is complete, the project must not claim that all dependency behavior has been proven network-silent.

Local processing reduces exposure to a remote service, but it does not make a device or recording anonymous.

## Storage, output, and deletion

The application does not intentionally write audio content or transcript text to a log. Transcript export uses a permission-restricted temporary file in the user-selected output directory and atomically moves it into place after success. A failure before export should leave no transcript output.

Process memory, operating-system swap, filesystem journals, temporary-file remnants, backups, snapshots, indexing, crash handling, antivirus tools, and third-party library caches may retain information. Deleting an input, output, or temporary file is not guaranteed secure deletion. Users control the source recording, model directory, and final output path and must protect and remove them according to their own risk environment.

## User responsibilities

Users must obtain appropriate consent and lawful authority before recording or transcribing another person. During pre-alpha development, do not use sensitive activist, witness, survivor, detainee, refugee, or confidential human-rights recordings. Use an updated device, avoid cloud-synced working folders, minimize identifying metadata, and manage model files, recordings, transcripts, shell history, and backups carefully.

## Limits

Idirak Safe cannot protect data when the device, operating system, runtime, model, or dependency is compromised. The current in-process backend is not sandboxed and has no CPU, memory, or operating-system network boundary. The project also cannot prevent observation of the screen or keyboard, malicious peripheral devices, seizure of an unlocked device, compelled disclosure, or physical coercion.

Transcription errors can create serious harms when text is treated as verified evidence. Every output is an experimental draft and must be reviewed against the audio by a qualified human.

No current pre-alpha build should be relied on for safety-critical or human-rights documentation work.

## Changes and questions

Privacy-relevant changes should update this file, [THREAT_MODEL.md](THREAT_MODEL.md), and the relevant release notes. Do not include sensitive personal information in a public issue. The private security contact will be confirmed before the first usable release; see [SECURITY.md](SECURITY.md).
