# Model Card

## Status

No transcription model has been selected, bundled, or released by Idirak Safe yet. This is a pre-alpha documentation template and evaluation plan, not a claim that a model with the properties below currently exists.

## Intended task

The planned task is automatic speech recognition for Uyghur audio, producing text locally on a user-controlled device. Intended users may include individuals, researchers, journalists, archivists, civil-society workers, and human-rights defenders who understand the risks and review outputs.

The project is not intended for speaker identification, biometric inference, mass surveillance, automated legal findings, automated credibility assessment, or decisions about a person's rights, safety, employment, immigration, or access to services.

## Model selection record

Before adding a model, maintainers must record:

- model name, version, source, and immutable identifier or hash;
- model and upstream code licences;
- architecture, parameter count, file size, and runtime requirements;
- training and evaluation data descriptions and provenance;
- supported scripts, dialects, audio formats, and platforms;
- quantization or other modifications;
- known safety, privacy, bias, and accuracy limitations; and
- all network connections or external services required.

Unknown provenance or incompatible licensing blocks release.

## Evaluation plan

Evaluation must use lawful, consented, appropriately licensed, non-sensitive data that is separated from training data. It should report more than one aggregate score and cover, where data and consent permit:

- word and character error rates;
- major Uyghur regional and diaspora speech varieties without treating one variety as inherently inferior;
- different ages and genders without attempting to infer those attributes;
- code-switching, named entities, numbers, and punctuation;
- varied microphones, compression, background noise, and speaking styles;
- hallucination, omission, repetition, and language-confusion rates;
- performance and memory on supported offline devices; and
- error patterns that could change the meaning of testimony or names.

Small or unrepresentative samples must be labelled. Results must include dataset details, confidence intervals where appropriate, and failure examples that contain no sensitive personal information.

## Expected limitations

Uyghur ASR may perform unevenly across dialects, accents, code-switching, rare names, technical vocabulary, emotional speech, poor recordings, and overlapping speakers. A fluent-looking transcript can still be wrong. Automated output must be treated as a draft and reviewed against the audio by a qualified human before consequential use.

Local execution does not make a model safe if the device, runtime, downloaded artifact, or surrounding workflow is compromised.

## Release gates

No model should be described as suitable for sensitive use until:

1. source, licence, provenance, and hashes are documented;
2. representative evaluations and material limitations are published;
3. offline behavior and storage/network claims are tested;
4. security and privacy reviews match the release claims;
5. safe installation, verification, and removal instructions exist; and
6. the corresponding data card is complete.

Each release must name any unmet gate and avoid claims that exceed the evidence.
