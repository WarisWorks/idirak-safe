# Security Policy

## Supported versions

Idirak Safe is pre-alpha. The repository contains an experimental CPU-only local ASR path, but no version is currently supported for sensitive, confidential, safety-critical, high-risk, or production use. Test only with synthetic, public-domain, or explicitly consented non-sensitive recordings. Supported versions and update timelines will be listed here before the first usable release.

## Current security controls

The experimental path currently:

- requires one explicitly named local backend and a pre-existing local model directory; `transcribe` has no model-download or remote fallback path;
- checks the pinned model manifest, exact file sizes, and SHA-256 hashes before opening audio;
- rejects model symlinks and common executable or pickle-based model formats, and requires Safetensors weights;
- loads processor and model files with `local_files_only=True` and `trust_remote_code=False`;
- forces `HF_HUB_OFFLINE`, `TRANSFORMERS_OFFLINE`, and `HF_DATASETS_OFFLINE` to `1`, disables Hugging Face telemetry, and sets `DO_NOT_TRACK=1` before importing those libraries;
- accepts only a regular, non-symlink, uncompressed WAV file no larger than 2 MiB and no longer than 30 seconds, with mono 16 kHz signed 16-bit PCM; and
- omits the source filename from a generated transcript and writes no transcript output when inference fails before export.

These controls are narrow and experimental. They have not been independently audited.

## Known security gaps

The CPU backend and third-party libraries execute in the main Python process. They are not confined by a built-in OS sandbox, subprocess boundary, firewall, or enforced CPU, memory, or execution-time limits. Offline environment variables and local-only loader options are not proof of OS-level network denial. One local macOS smoke test succeeded under a deny-network `sandbox-exec` profile, but it did not independently monitor attempted connections or establish cross-platform behavior. A compromised dependency, runtime, model-related configuration, operating system, or device can defeat application controls.

Installing dependencies and obtaining the model are separate setup actions. Those downloads are observable to network providers and hosting services even though `transcribe` itself does not download the model. Verify the pinned model after acquisition and do not use unverified files.

The application does not provide secure deletion. Process memory, swap, filesystem journals, caches, atomic-write remnants, backups, snapshots, crash handling, or indexing software may retain audio, paths, or transcripts. Do not use sensitive activist, witness, survivor, or confidential human-rights recordings during pre-alpha testing.

## Reporting a vulnerability

Do not open a public issue for a vulnerability or include exploit details, sensitive recordings, transcripts, credentials, or personal information in public discussions.

The intended private contact is `security@idirak.com`, but that mailbox must be confirmed as operational before the first public release. Until confirmation is recorded here, do not send sensitive vulnerability details to it. Contact the maintainer through the public profile linked in the repository and request a confirmed private reporting channel without disclosing the vulnerability itself.

When a private channel has been confirmed, a useful report includes:

- affected version, commit, and platform;
- a concise description of the impact;
- minimal reproduction steps using synthetic or non-sensitive data; and
- any suggested mitigation.

Never include real activist, witness, survivor, or other at-risk-person data in a report. Reproduce issues with synthetic or otherwise non-sensitive fixtures.

## Response targets

Formal response targets have not yet been established. Before the first supported release, this policy will state expected acknowledgement, triage, remediation, disclosure, and credit timelines.

## Disclosure

Please allow reasonable time to investigate and prepare a fix before public disclosure. A security advisory should describe the vulnerability and affected versions without exposing user data or unnecessarily enabling harm.

## Operational warning

Local processing is not a guarantee of privacy, confidentiality, anonymity, or safety. A compromised device, malicious dependency, insecure backup, unlocked session, physical access, network-observed setup download, or coercion can defeat application-level protections. See [THREAT_MODEL.md](THREAT_MODEL.md) for scope, current controls, release gates, and limits.
