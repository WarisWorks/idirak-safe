# Idirak Safe Roadmap

## Status and funding context

This is a proposed six-month development plan for a **US$10,000 funding request**. It does not state or imply that funding has been awarded by the Human Rights Foundation or any other funder. Scope, timing, and budget may change after technical research, community feedback, or a funding agreement.

The repository begins as a pre-alpha scaffold. There is no bundled ASR model or working transcription backend yet. Development will prioritize a small, reviewable local tool over broad feature coverage.

## Target outcome

At the end of the proposed period, the goal is to provide a testable command-line release that can import supported media, run a documented Uyghur ASR backend locally without a network connection, and export a user-controlled transcript. A release will not be described as safe for sensitive field use until its limitations and relevant security findings are documented.

## Proposed six-month work plan

### Month 1 — Scope, safety, and reproducible foundation

- Stabilize the Python package, CLI, transcript schema, and automated tests.
- Document the threat model, privacy boundaries, contribution process, and responsible disclosure route.
- Evaluate candidate local ASR engines and Uyghur models for accuracy, hardware needs, provenance, redistribution terms, and offline behavior.
- Define non-sensitive test fixtures and an evaluation protocol.

**Exit evidence:** a reproducible scaffold, backend comparison notes, licensing decision record, and baseline test report.

### Month 2 — Explicit local backend prototype

- Define a narrow backend interface between media import and transcript generation.
- Integrate one explicitly selected local backend if its licence and technical behavior are suitable.
- Fail closed when the backend or model is missing; never substitute a remote API.
- Record model version, configuration, and provenance with each generated transcript where practical.

**Exit evidence:** a local prototype demonstrated on non-sensitive test audio, or a public technical report explaining why the evaluated backends were unsuitable and the next implementation path.

### Month 3 — Uyghur transcript workflow

- Improve timestamp handling, Unicode normalization, punctuation options, and right-to-left display guidance.
- Complete deterministic exports to TXT, SRT, VTT, and JSON.
- Add model/data cards and an initial Uyghur evaluation set made only from licensed, public, synthetic, or explicitly consented non-sensitive material.
- Measure accuracy and document recurring failure modes rather than presenting a single unqualified score.

**Exit evidence:** repeatable evaluation results, documented sample provenance, and tested export compatibility.

### Month 4 — Privacy and reliability hardening

- Test operation with networking unavailable and add regression checks against accidental network access.
- Minimize temporary files, content-bearing logs, and retained metadata.
- Add malformed-input, resource-limit, failure-recovery, and unsafe-path tests.
- Arrange an independent privacy/security review within the available budget.

**Exit evidence:** an updated threat model, test results, remediation notes, and clearly listed unresolved risks.

### Month 5 — Cautious usability testing

- Prepare installation, offline-use, verification, and deletion guidance in accessible language.
- Conduct compensated review with a small group of relevant Uyghur-language users or civil-society advisers where this can be done safely.
- Use only synthetic, public, or explicitly consented non-sensitive test material.
- Prioritize changes that reduce dangerous misunderstandings, setup failures, or accidental disclosure.

**Exit evidence:** anonymized findings, consent and data-handling notes, and a public issue/decision summary that contains no participant identities or sensitive content.

### Month 6 — Pre-release and handoff

- Resolve release-blocking reliability, privacy, licensing, and documentation issues.
- Publish reproducible installation steps, checksums or provenance details for supported models, evaluation results, and known limitations.
- Tag a pre-release only if the documented acceptance checks pass.
- Publish a maintenance plan and a transparent summary of completed, deferred, and unsuccessful work.

**Exit evidence:** a versioned pre-release and release notes, or an honest final technical report if a responsible release is not yet possible.

## Proposed budget

| Category | Amount (USD) | Intended use |
| --- | ---: | --- |
| Lead developer compensation | $5,000 | Offline transcription engine, interface, packaging, and testing |
| Independent privacy/security review | $1,500 | Review of data flow, local-only claims, high-risk failure modes, and remediation verification |
| Uyghur linguistic quality assurance and tester honoraria | $1,200 | Language review and compensated, consent-based testing with non-sensitive material |
| Model conversion and benchmarking compute | $900 | Reproducible experiments and temporary non-sensitive evaluation storage |
| Low-resource test hardware and audio peripherals | $600 | Testing realistic local-device constraints and audio input behavior |
| Uyghur/English documentation and accessibility | $500 | Localization, safe-use guidance, and accessibility work |
| Release engineering and secure distribution | $300 | Code signing, checksums, packaging, and distribution costs |
| **Total requested** | **$10,000** | |

This is a planning estimate, not evidence of an award or authorization to spend grant funds.

## Release gates

A local transcription pre-release should not be promoted until all of the following are true:

- the selected engine, model, and required data have compatible and documented licences;
- transcription completes with networking disabled and has no silent remote fallback;
- installation and tests are reproducible on at least one documented reference environment;
- evaluation reports identify the test material, methodology, limitations, and material error modes;
- temporary-file and logging behavior is documented and tested;
- users receive clear warnings about manual verification and device-level risk; and
- no sensitive recordings, transcripts, credentials, or personal data are present in the repository or release artifacts.

## Out of scope for this six-month proposal

- cloud transcription or account-based hosted processing;
- claims of anonymity, forensic integrity, secure deletion, or guaranteed confidentiality;
- replacing professional security assessment, informed consent, or human transcript review;
- general-purpose AI chat, translation, OCR, or the existing hosted Idirak services; and
- collecting a large sensitive speech corpus.
