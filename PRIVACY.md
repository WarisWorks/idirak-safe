# Privacy

## Status

Idirak Safe is a pre-alpha project. It is not yet ready for sensitive, confidential, or high-risk material. This document describes the privacy properties the project intends to meet; it is not a claim that every property is already implemented or independently verified.

## Privacy goals

The project is being designed around these commitments:

- Transcription should run locally on a user's device by default.
- Audio and transcripts should not be uploaded to an Idirak server for normal transcription.
- Telemetry should be disabled by default. Any future diagnostics must be opt-in, documented, minimal, and free of audio or transcript content.
- Temporary files should be avoided where possible and clearly documented where unavoidable.
- Users should control where inputs, outputs, model files, and logs are stored.
- Network access should not be required after an explicitly initiated model download and installation.

The implementation, tests, and release notes must make clear which of these properties are available in each release.

## Data handling

No production data collection system or hosted transcription service is part of this repository at present. The repository must not contain or accept:

- recordings, transcripts, identities, or metadata from activists, witnesses, survivors, or other at-risk people;
- scraped private communications or material obtained through surveillance;
- data whose origin, licence, or consent cannot be demonstrated; or
- API keys, access tokens, device identifiers, or other secrets.

Examples and tests should use synthetic audio, public-domain material, or data supported by documented informed consent and an appropriate licence. See [docs/DATA_CARD.md](docs/DATA_CARD.md).

## Network and storage disclosures

Before a usable release, the project will document:

1. every network request the application can make;
2. the source, integrity check, licence, and size of each downloadable model;
3. all files, caches, logs, and configuration written to disk;
4. how users can delete local inputs, outputs, caches, and models; and
5. whether operating-system backups, crash reporters, indexing services, or cloud-synced folders may create additional copies.

Local processing reduces exposure to a remote service, but it does not make a device or recording anonymous.

## User responsibilities

Users must obtain appropriate consent and lawful authority before recording or transcribing another person. They should use an encrypted, updated device; avoid cloud-synced working folders for sensitive material; minimize identifying metadata; and securely manage exported transcripts and backups.

## Limits

Idirak Safe cannot protect data when the device, operating system, or model dependency is compromised. It also cannot prevent observation of the screen or keyboard, malicious peripheral devices, seizure of an unlocked device, compelled disclosure, or physical coercion. Transcription errors can create serious harms when text is treated as verified evidence; outputs must be reviewed by a qualified human.

No current pre-alpha build should be relied on for safety-critical or human-rights documentation work.

## Changes and questions

Privacy-relevant changes should update this file, [THREAT_MODEL.md](THREAT_MODEL.md), and the relevant release notes. Do not include sensitive personal information in a public issue. The private security contact will be confirmed before the first usable release; see [SECURITY.md](SECURITY.md).
