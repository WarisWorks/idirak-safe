# Threat Model

## Status and scope

Idirak Safe is a pre-alpha, local-first Uyghur transcription project. This threat model records design goals and release gates. It does not certify the current code as safe, audited, anonymous, or ready for use with sensitive human-rights material.

The intended workflow is local transcription of audio on a user-controlled device. A future release may support an explicit model download, but normal transcription should not require sending audio or transcripts to a remote service.

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

The project may rely on the user's device, operating system, package manager, model files, and third-party libraries. These are separate trust boundaries. Local execution does not eliminate risks from any compromised component.

## Threats and planned controls

| Threat | Planned control or release requirement |
| --- | --- |
| Audio or transcript sent to a server | Offline-default architecture; document and test all network behavior; no content telemetry |
| Unexpected files, logs, or caches | Document every persistent artifact; minimize temporary files; provide deletion guidance |
| Malicious or replaced model/package | Pin dependencies where practical; publish hashes and provenance; sign releases when a reliable process exists |
| Sensitive data exposed in crash reports | Disable third-party crash reporting by default; prohibit audio and transcript content in diagnostics |
| Metadata reveals identity or activity | Avoid collecting identifiers; document retained file metadata and export behavior |
| Inaccurate transcript causes harm | Publish evaluation limits; show uncertainty where supported; require human review for consequential use |
| Harmful contribution or test fixture enters repository | Review provenance, consent, licence, and sensitivity before merge; never accept sensitive activist recordings |
| Network observer learns a user obtained the tool/model | Support verifiable offline installation packages where feasible; document that downloads can still be observed |
| Dependency or build compromise | Maintain dependency inventory; use automated scanning and reproducible or verifiable builds where feasible |

## Explicitly out of scope

The project cannot reliably defend against:

- a compromised operating system, firmware, hardware, or already-unlocked device;
- physical surveillance, device seizure, compelled access, or physical coercion;
- a malicious person with access to exported files or backups;
- unsafe recording practices or lack of informed consent;
- identification of a speaker by a person who hears their voice; or
- every vulnerability in upstream models, runtimes, codecs, and operating-system components.

These limits must be visible in user documentation and must not be hidden behind a general claim of "offline" or "private."

## Misuse considerations

Speech recognition can be misused for surveillance, profiling, interrogation, or processing recordings obtained without consent. The project will not provide guidance or integrations intended for mass surveillance, speaker identification, or automated enforcement. Open-source licensing cannot prevent all misuse, so documentation and contribution review must be candid about this residual risk.

## Release gates

A release must not be described as suitable for sensitive use until maintainers have:

1. implemented and tested the documented offline-default path;
2. inspected network, storage, logging, and crash behavior;
3. documented model and dependency provenance and licences;
4. completed representative accuracy and failure-mode evaluation;
5. published deletion, verification, and safe-use instructions;
6. established a working private vulnerability-reporting channel; and
7. obtained an independent security review appropriate to the release's claims.

Any unmet gate must be identified in release notes.

## Review

Update this threat model when the architecture, supported platforms, model, data, network behavior, or intended users change. Security reports should follow [SECURITY.md](SECURITY.md).
