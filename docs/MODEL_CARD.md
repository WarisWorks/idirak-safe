# Model Card: Experimental `hf-wav2vec2` Backend

## Status

Idirak Safe `0.2.0a0` supports one experimental local model configuration. The model weights are not bundled. The upstream accuracy figures have not yet been independently reproduced by Idirak Safe, and this configuration is **not approved for sensitive, confidential, safety-critical, evidentiary, or production use**.

This card documents the model configuration accepted by the current code. It is not an endorsement of the model for human-rights work.

## Model identity

| Field | Value |
| --- | --- |
| Model ID | [`lucio/xls-r-uyghur-cv7`](https://huggingface.co/lucio/xls-r-uyghur-cv7) |
| Required revision | [`49339b194c6763d37414026456f7de09dd3f7554`](https://huggingface.co/lucio/xls-r-uyghur-cv7/tree/49339b194c6763d37414026456f7de09dd3f7554) |
| Architecture | `Wav2Vec2ForCTC`, fine-tuned from `facebook/wav2vec2-xls-r-300m` |
| Parameters | Approximately 300 million; the Hub reports 0.3B F32 parameters |
| Weight artifact | `model.safetensors`, 1,261,963,232 bytes |
| Weight SHA-256 | `aa923e217495329501fbea56cd3a8f695521a726525cb0c37ca143b1c262e2c6` |
| Runtime adapter | `hf-wav2vec2`, Hugging Face Transformers and PyTorch |
| Execution device | CPU only in Idirak Safe 0.2.0a0 |
| Input | Regular, non-symlinked, uncompressed mono 16 kHz signed PCM16 WAV, at most 30 seconds and 2 MiB |
| Decoder | Greedy CTC argmax followed by the local processor's `batch_decode` |
| Output | One unverified Uyghur (`ug`) Arabic-script text segment spanning the full audio duration |

Idirak Safe accepts the seven files and hashes identified in its packaged [SHA-256 manifest](../src/idirak_safe/model_manifests/lucio-xls-r-uyghur-cv7.json). `verify-model` must succeed before audio is opened.

## Selection rationale

This checkpoint was selected for the first bounded prototype because:

- it is specifically presented by its publisher as a Perso-Arabic Uyghur ASR fine-tune;
- a local smoke test of the exact revision produced Arabic-script Uyghur output;
- the Wav2Vec2 CTC path has simple, explicit greedy decoding and requires no language-prompt workaround;
- its weight is available as Safetensors;
- the publisher names the training/evaluation corpus and reports WER and CER; and
- the model, base model, and named dataset have permissive licence declarations from primary sources.

Selection for experimentation does not mean it is the most accurate available Uyghur model or suitable for field use. The current repository does not contain a completed, reproducible comparison against other candidates.

## Output representation

The [upstream model card](https://huggingface.co/lucio/xls-r-uyghur-cv7) says the vocabulary consists of Uyghur Perso-Arabic alphabetic characters and that punctuation was removed. The pinned `vocab.json` contains Uyghur Arabic-script letters, a word delimiter, and special unknown/padding tokens.

Idirak Safe does not add punctuation, capitalization, language-model rescoring, transliteration, translation, diarization, or post-processing. A readable Arabic-script result can still contain omissions, insertions, substitutions, incorrectly separated words, or meaning-changing errors.

## Offline runtime behavior

The model is downloaded separately by an explicit user action. During transcription, Idirak Safe:

1. verifies the local model directory against the packaged size and SHA-256 manifest;
2. sets Hugging Face and Transformers offline and telemetry-disable environment flags before importing those libraries;
3. loads `AutoProcessor` and `AutoModelForCTC` only from the local directory with `local_files_only=True` and `trust_remote_code=False`;
4. requires `use_safetensors=True` for model loading;
5. moves the model to CPU and uses PyTorch inference mode;
6. selects token IDs with `torch.argmax(logits, dim=-1)` and decodes them locally; and
7. returns one in-memory transcript segment before a user-selected local export.

The supported transcription command contains no download or remote inference path. This application-level control is not a general network sandbox and has not yet received an independent security review.

## Accuracy evidence

The upstream [model card](https://huggingface.co/lucio/xls-r-uyghur-cv7) and Hub evaluation metadata self-report the following Common Voice 7 results:

| Metric | Publisher-reported result |
| --- | ---: |
| Word error rate (WER) | 25.845% |
| Character error rate (CER) | 4.795% |

The same card states that the official Common Voice `train` and `dev` splits were combined for training and that the official `test` split was used both as validation data and for final evaluation. That method does not provide a clean, untouched final test set and may make the reported result less reliable as an estimate of unseen-speech performance.

The publisher explicitly describes the model as potentially useful only for low-fidelity tasks such as draft video captions and indexing recorded broadcasts. The publisher states that it is not reliable enough to replace live captions for accessibility.

Idirak Safe has not yet:

- independently reproduced the scores from the pinned revision;
- confirmed the exact text normalization and evaluation code;
- separated model selection from final evaluation on a clean test set;
- published uncertainty intervals or per-speaker/per-condition results;
- evaluated insertion, omission, substitution, empty-output, or word-boundary errors; or
- evaluated diaspora speech, dialects, field noise, compression, long-form audio, names, dates, numbers, negation, or code-switching.

The figures therefore cannot be generalized to sensitive recordings or treated as a safety claim.

## Local smoke-test evidence

The exact pinned model passed the packaged size and SHA-256 verification. On an 8 GB Apple Silicon Mac, one public CC0 Common Voice v24 Uyghur sample of 6.552 seconds:

| Observation | Result |
| --- | --- |
| Script | Arabic-script Uyghur output was produced |
| Wall time | 7.02 seconds |
| Maximum resident set size | 1,452,851,200 bytes, approximately 1.35 GiB, reported by `/usr/bin/time` |
| Network-denied run | The same output was reproduced under a macOS `sandbox-exec` profile denying all network access |

This is one functional smoke test. It is not an accuracy measurement, a representative performance benchmark, proof of portability, or a security audit. A Common Voice v24 sample also does not provide an independent out-of-domain accuracy test for a model trained on Common Voice 7. The sample and output remain local and ignored and must not be committed.

## Intended use in this release

Permitted experimental use is limited to local testing with synthetic, public, or explicitly consented non-sensitive Uyghur audio that satisfies the strict input format. Appropriate purposes include:

- exercising the local-only architecture;
- reproducing the upstream benchmark;
- measuring CPU runtime and memory;
- discovering error patterns; and
- testing the export workflow with an unverified draft.

Every output must be compared with the original audio by a qualified human before it is quoted, shared, indexed, or used in any consequential context.

## Prohibited or unsupported use

Do not use this release for:

- testimony, investigations, legal filings, emergency response, immigration matters, or decisions affecting a person's rights or safety;
- recordings containing identities, operational details, or information about activists, witnesses, survivors, detainees, refugees, or other at-risk people;
- live accessibility captions or a substitute for professional transcription;
- speaker identification, biometric inference, profiling, surveillance, or credibility assessment;
- automated publication, translation, redaction, fact finding, or evidence extraction; or
- any workflow in which a plausible but incorrect transcript could cause harm.

Open-source licensing cannot technically prevent misuse; these restrictions state the project's intended and supported use.

## Known technical limitations

- Audio is limited to one mono PCM16 WAV file of at most 30 seconds; there is no chunking or resampling.
- The entire recognition result becomes one segment. There are no word-level timestamps, confidence scores, speaker labels, or diarization.
- The vocabulary does not preserve punctuation.
- Greedy CTC decoding uses no external language model and may produce weak word boundaries or linguistically implausible output.
- The model may omit speech, insert text, substitute characters or words, confuse language content, or produce an empty result.
- Errors may be uneven across dialect, accent, age, gender, geography, speaking style, recording conditions, and code-switching. Idirak Safe has not measured those differences.
- Names, numbers, dates, quotations, and negation are especially consequential and require manual checking.
- CPU performance and memory have only one local smoke-test observation, not a supported-device benchmark.
- Hash verification identifies the pinned bytes; it does not detect bias, unsafe learned behavior, or problems inherited from training data.
- Local execution does not protect a compromised device or prevent copies in swap, backups, indexing, crash systems, or cloud-synced folders.

## Licence and provenance record

| Component | Recorded licence fact | Primary source | Caveat |
| --- | --- | --- | --- |
| Idirak Safe code | Apache License 2.0 | Repository [`LICENSE`](../LICENSE) | Applies to this project's source code, not third-party weights or data. |
| Fine-tuned checkpoint | Hugging Face metadata declares Apache-2.0 | [`lucio/xls-r-uyghur-cv7`](https://huggingface.co/lucio/xls-r-uyghur-cv7) | The pinned model file set contains no standalone `LICENSE` text; confirm redistribution obligations before bundling. |
| XLS-R 300M base checkpoint | Hugging Face metadata declares Apache-2.0 | [`facebook/wav2vec2-xls-r-300m`](https://huggingface.co/facebook/wav2vec2-xls-r-300m) | Preserve applicable notices and complete dependency review. |
| Mozilla Common Voice | Mozilla states Common Voice datasets are released under CC0 unless otherwise specified | [Common Voice legal terms](https://commonvoice.mozilla.org/terms) | Confirm the exact archived Common Voice 7 package and access terms used by the publisher before reproducing or redistributing data. |
| Hugging Face Transformers | Apache License 2.0 | [Official `LICENSE`](https://github.com/huggingface/transformers/blob/main/LICENSE) | A complete transitive dependency review remains outstanding. |

The pinned model repository also contains training/evaluation artifacts and pickle-based files that Idirak Safe neither downloads in its documented setup command nor loads. The project requests only the seven manifest files and reimplements the small inference adapter. This is a documentation record, not legal advice.

## Data relationship

The publisher identifies Mozilla Common Voice 7 Uyghur as the fine-tuning and evaluation data. Idirak Safe did not train this checkpoint, does not bundle Common Voice, and has not independently audited its samples. See the [data card](DATA_CARD.md) for the known facts, gaps, and evaluation rules.

## Required evaluation before broader use

1. Reproduce WER and CER using the pinned model revision, documented normalization, greedy decoding, and the stated Common Voice 7 splits.
2. Separate tuning/model selection from a clean final test set and report both the reproduced and corrected evaluation without obscuring the upstream figures.
3. Publish hashes, scripts, package versions, hardware, random settings, and all exclusions needed to repeat the result.
4. Evaluate licensed, non-sensitive data that does not overlap training, including diaspora varieties and realistic recording conditions.
5. Report WER, CER, empty outputs, insertion, omission, substitution, word-boundary, and manual high-impact error review.
6. Measure CPU-only load time, peak RAM, real-time factor, output stability, and failure behavior on documented reference devices.
7. Complete model, data, dependency, and redistribution review.
8. Complete independent privacy/security review and cautious user testing before considering any sensitive pilot.

Until every relevant gate is satisfied and documented, the model remains an experimental backend only.
