# Architecture

## Document status

This document separates the **implemented pre-alpha scaffold** from the **planned local transcription pipeline**. It is a design description, not a claim that audio transcription is already available.

## Security objective

Idirak Safe is intended to let a user create and export a Uyghur transcript on a device they control, without sending source media or transcript content to a hosted service. The core invariant is:

> A missing, broken, or unsupported local component causes an explicit failure. It must never trigger a silent network fallback.

Local execution narrows the data path but does not secure a compromised device, encrypt a disk, anonymize a user, guarantee secure deletion, or make inaccurate transcripts trustworthy.

## Data flow

```text
User-selected media
        |
        v
[1. Local import and validation]          planned
        |
        v
[2. Explicit local ASR backend]           planned; no backend bundled yet
        |
        v
[3. Canonical transcript document]        schema and validation implemented
        |
        v
[4. Local TXT / SRT / VTT / JSON export]  implemented
        |
        v
User-selected output path
```

There is no server-side processing stage in this design. Downloading installation dependencies or a model is a separate setup action that must be explicit and documented; transcription itself must not require a network connection.

## Current implementation

The initial Python scaffold provides:

- `idirak-safe doctor`, which reports that the project is pre-alpha, local-only, and has no ASR backend;
- parsing and validation for an existing local transcript JSON document;
- deterministic export to TXT, SRT, VTT, and normalized JSON; and
- unit tests for implemented behavior.

It does not currently import audio, decode media, run inference, or generate a transcript. A transcription request must fail clearly while no backend is implemented.

## Planned components

### 1. Local importer

The importer will receive a path explicitly selected by the user. Its responsibilities are expected to include:

- rejecting unsupported or malformed inputs with a clear error;
- extracting only the audio stream and metadata necessary for transcription;
- bounding input size, duration, decoding time, and temporary storage where practical;
- avoiding content-bearing logs; and
- keeping temporary work inside a documented, user-controlled or securely permissioned location.

Media parsers and codecs expand the attack surface. Their versions and provenance must be documented, and malformed-file behavior must be tested. Automatic upload, URL import, cloud storage discovery, and background indexing are outside the core design.

### 2. Local ASR backend boundary

The CLI will require an explicitly configured local backend. The backend adapter should accept decoded local audio plus explicit options and return timestamped segments. It must not accept a remote API as an automatic substitute.

Expected failure behavior:

- no backend installed: explain how to install or configure a supported local option, then exit non-zero;
- no compatible model present: name the missing local requirement, then exit non-zero;
- backend crash or resource exhaustion: preserve the original media, avoid a misleading partial-success status, then exit non-zero; and
- network unavailable: local inference continues normally; if it cannot, that backend is not acceptable for the local-only release profile.

A supported backend must have documented source, licence, version, model provenance, hardware requirements, offline behavior, and known accuracy limitations. Model files should be identified using stable versions and checksums where distribution permits.

### 3. Canonical transcript document

The internal handoff between ASR and exporters is a small JSON-compatible document. Its minimum shape is:

```json
{
  "language": "ug",
  "source": "interview-01.wav",
  "segments": [
    {
      "start": 0.0,
      "end": 2.4,
      "text": "سالام دۇنيا",
      "speaker": "optional-user-label"
    }
  ]
}
```

`language` defaults to `ug`. `source` and `speaker` are optional. `segments` must be non-empty, timestamps must be valid and ordered, and `text` must be present. Future schema changes should be versioned before they would make older documents ambiguous.

The source value can reveal a filename or workflow detail. A future privacy option should allow it to be omitted or replaced before export.

### 4. Exporters

Exporters transform the canonical document locally into:

- plain UTF-8 text for review and editing;
- SRT or VTT captions with timestamps; or
- normalized JSON for structured workflows.

The output path is always supplied by the user. Export should be deterministic for the same validated input and options. Exporters do not correct recognition errors and must not imply that the transcript has been human-verified.

## Network policy

The core Python scaffold uses no network service and emits no telemetry. Planned transcription code must preserve that property at runtime.

The design prohibits:

- automatic fallback from local inference to a hosted API;
- automatic uploading of crash reports, analytics, media, prompts, or transcripts;
- fetching a model when the user starts a transcription; and
- remote licence checks or authentication required to transcribe.

If optional setup tooling can download a dependency or model, the action must be user-initiated, show its source and expected size, verify integrity where possible, and be separable from transcription. Tests should exercise the supported workflow with networking unavailable.

## Data lifecycle

```text
Original media       remains at the user-selected path
Temporary audio      created only when necessary; location and cleanup documented
Transcript state     held in memory where practical or written only by explicit action
Exports              written to a user-selected path
Logs                  operational metadata only; no transcript or media content by default
Telemetry             none
```

Process termination, operating-system caching, swap, backups, filesystem snapshots, and storage-device behavior can leave recoverable copies. The application cannot promise secure deletion. Users operating under elevated risk need device and operational-security practices outside this project's scope.

## Trust boundaries and dependencies

- **Trusted for a run:** the user's device, operating system, installed Idirak Safe release, explicitly selected backend, local model, and output destination.
- **Untrusted inputs:** media files, transcript JSON, filenames, embedded metadata, and third-party model packages.
- **External dependencies:** Python, media decoders, ASR runtime, and model artifacts. Each introduces supply-chain and parser risk.
- **Humans remain in the loop:** generated text requires review, especially for names, dates, negation, dialectal speech, and evidence used in consequential decisions.

Release documentation should pin or bound supported versions, record licences and hashes where practical, and list unresolved risks. See `THREAT_MODEL.md` for the adversary and abuse analysis.

## Planned verification

The architecture should be backed by tests and evidence, including:

- unit tests for schema validation and every exporter;
- integration tests that run the selected backend on non-sensitive fixtures;
- network-denial tests proving the supported transcription path completes offline;
- tests for malformed files, unsafe paths, interruptions, and resource exhaustion;
- inspection of logs and temporary directories for content leakage;
- reproducible accuracy evaluation with documented data provenance; and
- an independent focused privacy/security review before recommending sensitive pilot use.

Until these checks exist and their results are published, Idirak Safe remains pre-alpha and unsuitable for sensitive material.
