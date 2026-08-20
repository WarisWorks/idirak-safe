# Idirak Safe Roadmap

## Status and funding context

This is a proposed six-month development plan for a **US$10,000 funding request**. It does not state or imply that funding has been awarded by the Human Rights Foundation or any other funder. Scope, timing, and budget may change after technical research, community feedback, or a funding agreement.

The independently initiated `0.2.0a0` pre-alpha milestone already includes a strict short-WAV importer, one checksum-pinned experimental `hf-wav2vec2` backend, hard-offline local loading, and local exports. That milestone is evidence of feasibility, not evidence of field readiness or an award.

The selected experimental checkpoint is [`lucio/xls-r-uyghur-cv7`](https://huggingface.co/lucio/xls-r-uyghur-cv7) at revision `49339b194c6763d37414026456f7de09dd3f7554`. Its weights are not bundled. Its publisher describes it as suitable only for low-fidelity draft captions or indexing and reports WER `25.845%` and CER `4.795%` on Common Voice 7. Idirak Safe has not independently reproduced those results and does not approve the model for sensitive use.

## Current technical baseline

Implemented before the proposed funded period:

- Python package, command-line interface, strict transcript schema, and deterministic TXT/SRT/VTT/JSON exporters;
- validation of regular, non-symlinked, mono 16 kHz signed PCM16 WAV files up to 30 seconds and 2 MiB;
- one allowlisted CPU-only Hugging Face Wav2Vec2/XLS-R CTC backend;
- exact model revision and SHA-256 manifest verification before audio is opened;
- local-only Safetensors loading with offline flags, remote code disabled, and no transcription-time download or remote API;
- one public, non-sensitive 6.552-second smoke sample that produced Arabic-script output on an 8 GB Apple Silicon Mac in 7.02 seconds with approximately 1.35 GiB maximum resident memory, including the same output under a network-denied macOS sandbox; and
- unit coverage for validation, verification, local loader options, failures, and output behavior.

Still unproven or incomplete:

- independent WER/CER reproduction and evaluation outside the reported Common Voice conditions;
- diaspora, dialect, noise, code-switching, long-form, names, dates, numbers, and negation testing;
- CPU runtime, peak-memory, and low-resource-device benchmarks;
- repeatable automated and cross-platform network-denial coverage beyond the one smoke run, plus storage-leakage tests;
- a complete third-party dependency and redistribution review;
- segment or word timestamps, chunking, media conversion, and a review interface; and
- independent privacy/security review or approval for sensitive use.

## Target outcome

At the end of the proposed period, the goal is a reproducibly evaluated command-line pre-release that imports documented local audio formats, runs a selected Uyghur ASR backend without network access, and exports a user-controlled draft transcript. It will not be described as safe for sensitive field use unless the relevant accuracy, usability, privacy, security, data, and licensing gates are actually satisfied.

An honest technical report is an acceptable outcome if testing shows that the model or workflow is not responsible to release more broadly.

## Proposed six-month work plan

### Month 1 — Reproducible model baseline

- Reproduce or refute the upstream WER `25.845%` and CER `4.795%` with the pinned revision, documented normalization, and a clean Common Voice 7 test procedure.
- Publish model file hashes, runtime versions, scripts, hardware, exclusions, and result limitations.
- Benchmark CPU load time, peak RAM, real-time factor, and failure behavior on documented reference systems.
- Complete an initial dependency, model, base-model, and dataset licence inventory.
- Compare at least one responsibly licensed alternative backend against the same non-sensitive protocol.

**Exit evidence:** reproducible evaluation scripts and results, hardware measurements, a candidate comparison, and a licensing/provenance decision record.

### Month 2 — Accuracy and data-quality study

- Build a small evaluation set only from licensed public or explicitly consented non-sensitive material, with documented provenance and speaker-disjoint splits.
- Evaluate diaspora speech varieties, realistic microphones, noise, code-switching, names, dates, numbers, negation, omissions, and substitutions where the data responsibly permits.
- Report WER and CER alongside empty-output, insertion, omission, and high-impact semantic error analysis.
- Decide transparently whether to retain, replace, or support multiple local model backends.

**Exit evidence:** a versioned data card, evaluation report, model decision, and public limitations that do not expose participants.

### Month 3 — Usable local transcript workflow

- Add bounded chunking and timestamp handling only after failure behavior is understood.
- Evaluate safe local conversion for selected media formats without enabling URL import or cloud discovery.
- Improve Uyghur right-to-left review guidance, Unicode handling, punctuation workflow, and deterministic exports.
- Record model identity, revision, configuration, and verification status in structured output without copying sensitive source metadata by default.

**Exit evidence:** a tested end-to-end local workflow on non-sensitive fixtures, versioned output schema, and compatibility tests.

### Month 4 — Privacy and reliability hardening

- Run the complete supported workflow with networking denied at the operating-system level and add regression tests against network access.
- Inspect temporary files, permissions, logs, caches, process environment, crash behavior, interruptions, and failure recovery.
- Add malformed-input, resource-limit, unsafe-path, model-tampering, and output-integrity tests.
- Arrange an independent focused privacy/security review within the available budget.

**Exit evidence:** updated architecture and threat model, test artifacts, review findings, remediation notes, and clearly listed unresolved risks.

### Month 5 — Cautious usability and language review

- Prepare installation, offline-use, verification, review, retention, and deletion guidance in accessible Uyghur and English.
- Conduct compensated review with a small group of relevant Uyghur-language users or civil-society advisers only where participation can be safe and voluntary.
- Use synthetic, public, or explicitly consented non-sensitive test material; do not collect operational human-rights audio.
- Prioritize changes that reduce dangerous misunderstandings, setup failures, accidental disclosure, and over-trust in generated text.

**Exit evidence:** anonymized findings, consent and data-handling records, language QA notes, and a public decision summary containing no participant identities or sensitive content.

### Month 6 — Release decision and handoff

- Resolve release-blocking accuracy, reliability, privacy, licensing, documentation, and usability findings.
- Publish reproducible installation, model verification, evaluation, offline-use, and known-limitation materials.
- Tag a pre-release only if the documented acceptance gates pass.
- Publish a maintenance plan and a transparent summary of completed, deferred, unsuccessful, and blocked work.

**Exit evidence:** a versioned pre-release with evidence and release notes, or an honest final technical report explaining why a responsible broader release is not yet possible.

## Proposed budget

| Category | Amount (USD) | Intended use |
| --- | ---: | --- |
| Lead developer compensation | $5,000 | Offline transcription engine, evaluation workflow, interface, packaging, and testing |
| Independent privacy/security review | $1,500 | Review of data flow, local-only claims, high-risk failure modes, and remediation verification |
| Uyghur linguistic quality assurance and tester honoraria | $1,200 | Language review and compensated, consent-based testing with non-sensitive material |
| Model conversion and benchmarking compute | $900 | Reproducible experiments and temporary non-sensitive evaluation storage |
| Low-resource test hardware and audio peripherals | $600 | Testing realistic local-device constraints and audio input behavior |
| Uyghur/English documentation and accessibility | $500 | Localization, safe-use guidance, and accessibility work |
| Release engineering and secure distribution | $300 | Code signing, checksums, packaging, and distribution costs |
| **Total requested** | **$10,000** | |

This is a planning estimate, not evidence of an award or authorization to spend grant funds.

## Release gates

A local transcription pre-release must not be promoted for sensitive use until all applicable gates are satisfied:

- selected engine, model, base model, runtime, and data licences and provenance are documented and reviewed;
- required model artifacts are pinned and verified, and redistribution choices match their terms;
- upstream scores are independently reproduced or corrected, and broader evaluation reports identify data, methods, uncertainty, and material error modes;
- transcription completes with networking denied and has no silent remote fallback;
- installation and inference are reproducible on documented CPU-only reference environments;
- model download, temporary files, logs, permissions, caches, failure recovery, and deletion limits are documented and tested;
- independent privacy/security findings are resolved or clearly disclosed;
- users receive prominent warnings and a mandatory human-review workflow; and
- no sensitive recordings, transcripts, credentials, or personal data are present in the repository, test artifacts, evaluation release, or package.

Passing technical tests alone will not establish that processing a particular recording is lawful, ethical, or safe.

## Out of scope for this six-month proposal

- cloud transcription or account-based hosted processing;
- mass surveillance, speaker identification, biometric profiling, or automated credibility assessment;
- claims of anonymity, forensic integrity, secure deletion, guaranteed confidentiality, or perfect accuracy;
- replacing professional security assessment, informed consent, or qualified human transcript review;
- general-purpose AI chat, translation, OCR, or the existing hosted Idirak services; and
- collecting a large sensitive speech corpus.
