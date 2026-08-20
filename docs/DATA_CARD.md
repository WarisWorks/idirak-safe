# Data Card

## Status

Idirak Safe currently publishes no training, evaluation, or demonstration dataset. No sensitive human-rights recordings should be added to this repository. This document defines the evidence and safeguards required before any dataset or data-derived artifact is used or released.

## Prohibited data

Do not collect, contribute, process for development, or publish:

- activist, witness, survivor, detainee, refugee, or other at-risk-person recordings or transcripts;
- intercepted, leaked, covertly recorded, or surveillance-derived material;
- private messages, calls, meetings, or archives without specific informed consent;
- scraped audio or text when the terms, reasonable expectations, or licence do not permit the intended use;
- biometric or identifying metadata unnecessary for transcription research; or
- material whose provenance, consent, or legal right to use cannot be verified.

Public availability alone does not establish ethical permission for model training or evaluation.

## Permitted sources

Early tests should prefer synthetic speech, recordings created specifically for testing with informed consent, or clearly licensed public-domain material. A source may be considered only after documenting:

- creator, collector, and current steward;
- collection date, place at an appropriately safe level of precision, and method;
- original purpose and proposed new use;
- informed-consent language and how consent was recorded;
- licence and any restrictions on training, evaluation, redistribution, or commercial use;
- compensation and community involvement, where applicable;
- retention, access control, withdrawal, and deletion procedures; and
- known demographic, dialect, geographic, technical, and content limitations.

## Data minimization

Collect only what is necessary for a documented purpose. Avoid names and precise locations. Remove unnecessary metadata and restrict access to raw material. De-identification must be assessed case by case: a voice, story, or linguistic detail can remain identifying after names are removed.

Consent must be specific, understandable, voluntary, and appropriate to the foreseeable use. It must not be assumed from silence or from unrelated publication. A withdrawal process must explain what can be removed from raw data, derived datasets, trained models, caches, and prior releases—and candidly state where complete removal is technically impossible.

## Dataset documentation

Before use, create a versioned record containing:

- dataset name, version, owner, licence, and cryptographic hash;
- inclusion and exclusion rules;
- collection, annotation, quality-control, and filtering methods;
- number and duration of recordings, transcript volume, and splits;
- permitted purposes and prohibited uses;
- access controls and deletion schedule;
- consent and withdrawal status;
- known representational gaps and foreseeable harms; and
- the relationship between training, validation, and test sets.

Training and evaluation speakers and recordings must be kept separate to prevent leakage. Deduplication checks and contamination risks must be documented.

## Release gates

No dataset or data-derived model may be published through this project until:

1. provenance, licence, consent, and intended use are documented and reviewed;
2. sensitive and prohibited content checks are complete;
3. access, retention, withdrawal, and deletion processes are operational;
4. the dataset's limitations and representational gaps are published;
5. training/evaluation leakage checks are complete; and
6. release has received explicit maintainer approval following privacy and security review.

If a requirement cannot be verified, the data must not be used or released.
