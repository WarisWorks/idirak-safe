# Contributing to Idirak Safe

Thank you for helping build accessible, privacy-preserving Uyghur transcription software. The project is pre-alpha, and safety and honesty take priority over feature speed.

## Before contributing

Open an issue for a substantial change so its scope, privacy impact, and licensing can be discussed. Do not put vulnerabilities, secrets, personal data, or sensitive human-rights information in a public issue; follow [SECURITY.md](SECURITY.md) instead.

## Contribution workflow

1. Fork the repository and create a focused branch.
2. Make the smallest coherent change.
3. Add or update tests and documentation.
4. Run the documented checks once they are available.
5. Explain behavior, privacy, security, model, data, and dependency changes in the pull request.

The project does not yet promise a stable API or file format.

## Data and examples

Never contribute sensitive activist recordings, testimony, intercepted material, private communications, personal information, credentials, or data of unknown origin.

Audio, text, and annotations may be contributed only when their provenance, licence, consent, permitted uses, retention, and withdrawal process are documented. Prefer synthetic data or clearly licensed public-domain material. De-identification alone does not establish consent or make a voice recording safe to publish. See [docs/DATA_CARD.md](docs/DATA_CARD.md).

## Models and dependencies

A model or dependency contribution must document:

- its exact source and version;
- applicable software, model, and data licences;
- hashes or another integrity-verification method where practical;
- runtime, storage, and network behavior;
- known limitations and relevant evaluation evidence; and
- whether it introduces telemetry, remote execution, or external services.

Do not add a model trained on data of unknown provenance or incompatible terms. Update [docs/MODEL_CARD.md](docs/MODEL_CARD.md), [PRIVACY.md](PRIVACY.md), and [THREAT_MODEL.md](THREAT_MODEL.md) when applicable.

## Privacy and safety review

Changes that affect networking, storage, logs, crash handling, model downloads, audio decoding, exports, or permissions require explicit privacy and security review. Tests must use synthetic or appropriately licensed non-sensitive fixtures.

## Licence

Unless clearly stated otherwise, contributions intentionally submitted to this repository are licensed under the Apache License 2.0 in [LICENSE](LICENSE). By contributing, you confirm that you have the right to submit the work under those terms.
