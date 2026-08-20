# Threat Model

## Status and scope

Idirak Safe is a pre-alpha, local-first Uyghur transcription project. An experimental CPU-only Hugging Face Wav2Vec2/CTC path using the pinned `lucio/xls-r-uyghur-cv7` model now exists for short, strictly formatted local audio. This threat model records implemented application controls, known gaps, and release gates. It does not certify the code as safe, audited, anonymous, or ready for sensitive human-rights material.

The intended workflow is local transcription of audio on a user-controlled device. Model acquisition is a separate setup action. The `transcribe` command requires a pre-existing verified local model and contains no model download or remote-ASR fallback.

## Assets to protect

- source audio and transcripts;
- names, voices, locations, timestamps, and other identifying metadata;
- information about which files were processed;
- model and application configuration;
- encryption keys, credentials, and signing keys; and
- the safety and identity of users, speakers, witnesses, and collaborators.

## Intended users

Potential users include Uyghur-language researchers, journalists, archivists, civil-society workers, and human-rights defenders. Some may face targeted surveillance, device seizure, network monitoring, phishing, or coercion. High-risk users should not use a pre-alpha release.

## Trust boundaries

The experimental backend runs on the CPU inside the main Python process. The user's device, operating system, Python environment, PyTorch, Transformers, Hugging Face, NumPy, Safetensors, model files, and packaging sources are separate trust boundaries. The application does not provide an OS sandbox or subprocess boundary. One local macOS run succeeded under a deny-network `sandbox-exec` profile, but it did not independently monitor attempted connections and does not prove network silence across supported platforms. Local execution does not eliminate risks from a compromised component.

## Implemented controls and residual risks

| Threat | Current control | Residual risk or release requirement |
| --- | --- | --- |
| Silent upload or model download during transcription | Explicit `hf-wav2vec2` allowlist; no hosted fallback or download path; Hugging Face/Transformers offline environment forced before import; `local_files_only=True`; `trust_remote_code=False`; one macOS deny-network smoke run succeeded | These are in-process controls, not built-in OS-enforced network isolation. A repeatable test that monitors attempted connections across supported platforms and an independent review are still required. |
| Malicious, replaced, or executable model | The model revision is pinned; required files are size- and SHA-256-verified before audio is opened; symlinks and common executable/pickle formats are rejected; weights load with Safetensors | Dependencies and the in-process runtime remain trusted. Signing, dependency locking, broader supply-chain review, and sandboxing remain release work. |
| Malformed or excessive media | Input is restricted to a regular non-symlink WAV file, at most 2 MiB and 30 seconds, mono 16 kHz signed PCM16; malformed and truncated input fails | Media parsing and inference still occur in the main process without CPU or memory isolation. Fuzzing and resource-exhaustion testing remain required. |
| Filename or workflow metadata in transcript | The generated canonical transcript omits the source filename | Input/output paths can remain visible in command-line arguments, shell history, process inspection, filesystem metadata, and backups. |
| Unexpected temporary or retained data | Decoded PCM is held in process memory; the adapter does not intentionally create decoded-audio files or content logs; transcript output is created only after successful inference | Memory, swap, journals, atomic-write temporary remnants, caches, crash artifacts, antivirus/indexing, snapshots, and backups may retain data. Secure deletion is not provided. |
| Observer learns that a model or dependency was obtained | Transcription uses a pre-existing local model and does not download | Separate setup downloads are observable to the network provider and host. Offline side-loading and safer acquisition guidance remain needed. |
| Inaccurate transcript causes harm | Output is labelled an experimental draft and human review is required | Representative Uyghur accuracy and failure-mode evaluation is incomplete; no consequential use is appropriate. |
| Harmful test data enters the project | Documentation prohibits sensitive activist recordings and requires provenance, consent, and licensing | Maintainer review and automated repository/release checks remain necessary. |

## Explicitly out of scope

The project cannot reliably defend against:

- a compromised operating system, firmware, hardware, or already-unlocked device;
- physical surveillance, device seizure, compelled access, or physical coercion;
- a malicious person with access to exported files or backups;
- unsafe recording practices or lack of informed consent;
- identification of a speaker by a person who hears their voice; or
- every vulnerability in upstream models, runtimes, codecs, and operating-system components.

It also does not currently provide an OS network sandbox, process isolation, CPU or memory quotas, secure deletion, anonymity, or protection from network observation during a separate model or dependency download.

These limits must be visible in user documentation and must not be hidden behind a general claim of "offline" or "private."

## Misuse considerations

Speech recognition can be misused for surveillance, profiling, interrogation, or processing recordings obtained without consent. The project will not provide guidance or integrations intended for mass surveillance, speaker identification, or automated enforcement. Open-source licensing cannot prevent all misuse, so documentation and contribution review must be candid about this residual risk.

## Release gates

A release must not be described as suitable for sensitive use until maintainers have:

1. completed repeatable OS-level no-network tests that detect attempted connections by the full supported runtime, not only application mocks, across supported platforms;
2. evaluated process isolation and enforced CPU, memory, execution-time, and output limits;
3. fuzzed WAV parsing and tested malformed input, model tampering, interruption, disk failure, and cleanup behavior;
4. inspected logs, memory-related risks, caches, temporary paths, crash behavior, and release artifacts using non-sensitive canary data;
5. locked and reviewed dependencies and documented the model, training-data provenance, licences, pinned revision, and hashes;
6. completed representative Uyghur accuracy and failure-mode evaluation using only appropriately licensed, consented, non-sensitive data;
7. published model acquisition, offline verification, deletion-limit, and safe-use instructions, including the observability of setup downloads;
8. established a working private vulnerability-reporting channel; and
9. obtained an independent security and privacy review appropriate to the release's claims.

Any unmet gate must be identified in release notes.

## Review

Update this threat model when the architecture, supported platforms, backend, model, data, dependency, network behavior, input limits, or intended users change. Security reports should follow [SECURITY.md](SECURITY.md). Until every relevant gate is met, use only non-sensitive recordings and retain the pre-alpha warning.
