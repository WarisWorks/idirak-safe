# Data Card

## Status

Idirak Safe `0.2.0a0` publishes no training dataset, evaluation dataset, demonstration audio, or human-rights recording. The repository contains only synthetic text fixtures and mocked or synthetic audio test data. The project did not train the selected model and has not independently reproduced its upstream evaluation.

The current command can process a user-selected local WAV file, but that file is runtime input, not a dataset collected by Idirak Safe. Version 0.2.0a0 is not approved for sensitive data.

## Data inventory

| Data category | Included or collected by Idirak Safe? | Current role |
| --- | --- | --- |
| Mozilla Common Voice 7 Uyghur | No | Named by the upstream publisher as the selected model's fine-tuning and evaluation data |
| Independent Uyghur evaluation set | No | Required future work |
| Public CC0 Common Voice v24 smoke sample | No; remains local and ignored | One 6.552-second functional and network-denial smoke test, not an accuracy test |
| Repository audio fixtures | No human speech | Parser tests use small synthetic WAV bytes; inference tests use mocks |
| User-selected runtime WAV | Processed locally for the current command; not collected by the project | Converted to an in-memory sample array for one transcription run |
| Generated transcript | Written only to a user-selected path | Unverified draft output |
| Hosted analytics or telemetry data | No | No collection path exists |

## Upstream Common Voice 7 record

The selected model's [upstream model card](https://huggingface.co/lucio/xls-r-uyghur-cv7) records these facts:

- base checkpoint: `facebook/wav2vec2-xls-r-300m`;
- fine-tuning dataset: Mozilla Common Voice 7.0 Uyghur (`ug`);
- training data: the official `train` and `dev` splits combined;
- validation and final evaluation data: the official `test` split used for both;
- output representation: Uyghur Perso-Arabic alphabetic characters with punctuation removed; and
- intended model scope: low-fidelity draft captions and indexing, not reliable live accessibility captions.

Mozilla's current [Common Voice legal terms](https://commonvoice.mozilla.org/terms) state that Common Voice datasets are released under the CC0 public-domain dedication unless otherwise specified. The terms also describe contributor assurances concerning original creation, third-party rights, and acceptable use.

Idirak Safe does not download, mirror, package, or redistribute Common Voice 7. Before reproducing the upstream evaluation, the project must confirm the exact archived version, files, hashes, licence notice, and access terms applicable to that release instead of assuming that current distribution details are identical.

## Known upstream documentation and methodology gaps

The model card identifies the corpus and splits but is not a complete data-governance record. Idirak Safe has not yet independently verified:

- the exact Common Voice 7 archive, checksum, Uyghur sample counts, audio duration, and speaker counts used;
- participant-consent and privacy notices applicable when that release was collected;
- withdrawal, deletion, moderation, and quality-control processes for the archived release;
- speaker separation, duplicate recordings, or leakage across `train`, `dev`, and `test`;
- dialect, geography, age, gender, device, and recording-condition distributions;
- normalization rules used before calculating WER and CER; or
- overlap between Common Voice 7 and later Common Voice releases used for smoke testing or future evaluation.

The upstream card states that the official `test` split was used for validation as well as final evaluation. Because model selection and final reporting were not cleanly separated, the published score may be optimistic for unseen speech and must be reproduced before interpretation.

Absence of details from the model card is not evidence that consent or safeguards were absent. It means Idirak Safe has not verified them and must not imply more than primary documentation supports.

## Upstream evaluation evidence

The publisher self-reports WER `25.845%` and CER `4.795%` on Common Voice 7. Idirak Safe has not independently reproduced those figures, audited the split, or confirmed the normalization and evaluation implementation.

These figures describe one upstream test setting. They do not establish performance on diaspora speech, regional varieties, code-switching, long-form material, phone recordings, field noise, overlapping speech, emotional speech, names, dates, numbers, negation, or sensitive testimony.

See the [model card](MODEL_CARD.md) for technical and accuracy limitations.

## Local smoke-test sample

One public CC0 Common Voice v24 Uyghur sample lasting 6.552 seconds was used locally to confirm that:

- the exact pinned model passes the packaged SHA-256 verification;
- the backend produces Arabic-script Uyghur output;
- transcription can complete with all network access denied by a macOS `sandbox-exec` profile; and
- the same local input produces the same observed text in the normal and network-denied smoke runs.

The sample and generated output remain ignored and must not be committed. A single sample from a later Common Voice release is not an accuracy evaluation, an independent domain, a representative population, or evidence that the transcript was correct. It must not be added to a future evaluation result without checking duplication and overlap with model training data.

## Runtime data handling

For `transcribe`, version 0.2.0a0 accepts only a regular, non-symlinked, uncompressed mono WAV containing signed 16-bit PCM at exactly 16 kHz. The file must be non-empty, at most 30 seconds, and at most 2 MiB.

The implemented lifecycle is:

1. verify the local model before opening audio;
2. validate the WAV header, file type, size, and frame count;
3. read PCM bytes and convert them to a normalized sample array in process memory;
4. run CPU-only CTC inference using local verified model files;
5. hold one generated transcript segment in memory; and
6. write the requested TXT, SRT, VTT, or JSON output to a user-selected local path.

The command does not upload audio, send transcript content, fetch remote models, create an intermediate decoded-audio file, or add the source filename to an ASR-generated transcript. It does not delete the original audio or final output. Operating-system swap, backups, snapshots, indexing, crash handling, shell history, and cloud-synced folders are outside the application's control and can retain metadata or copies.

## Data prohibited from project development

Do not collect, contribute, use for testing, or publish:

- activist, witness, survivor, detainee, refugee, or other at-risk-person recordings or transcripts;
- testimony, operational discussions, private calls, meetings, or archives;
- intercepted, leaked, covertly recorded, scraped, or surveillance-derived material;
- recordings made without specific informed consent and lawful authority for the proposed use;
- data whose provenance, licence, or permitted uses cannot be verified;
- biometric or identifying metadata unnecessary for a documented evaluation; or
- material whose possession, publication, error analysis, or breach could endanger a person.

Public availability alone does not establish ethical permission. De-identification alone is insufficient because a voice, story, location, or linguistic detail can remain identifying.

## Permitted non-sensitive evaluation sources

Early evaluation may use only:

- synthetic signals for parser and failure-path tests;
- recordings created specifically for evaluation under documented, voluntary, informed consent;
- clearly licensed public speech whose reuse is ethically appropriate; or
- upstream benchmark material after licence, access, split, contamination, and documentation review.

Before any human speech is used, record:

- creator, collector, steward, version, stable source, and cryptographic hashes;
- licence and restrictions on training, evaluation, redistribution, and commercial use;
- collection purpose, proposed new use, and exact consent language;
- compensation, community involvement, retention, access, withdrawal, and deletion processes;
- number and duration of recordings, speakers, annotations, and splits;
- speaker-disjoint and recording-disjoint split controls;
- inclusion, exclusion, normalization, and quality-control decisions; and
- known representational gaps and foreseeable harms.

Public evaluation artifacts must contain no sensitive personal information or uniquely identifying failure examples.

## Planned independent evaluation

The first reproducible evaluation should:

1. pin the model revision, all seven file hashes, runtime versions, greedy CTC decoding, hardware, and normalization code;
2. reproduce or refute the upstream Common Voice 7 WER and CER without altering the reported result;
3. distinguish reproduction on the publisher's reused validation/test split from a clean final evaluation;
4. use speaker-disjoint, uncontaminated, licensed non-sensitive test sets beyond model training data;
5. report WER and CER alongside empty output, insertion, omission, substitution, and word-boundary error rates;
6. manually review errors involving names, numbers, dates, negation, and meaning-changing substitutions;
7. stratify results by recording condition and speech variety only where data, consent, and sample size support a responsible comparison; and
8. publish limitations, exclusions, sample counts, and uncertainty instead of one unqualified score.

No private sensitive recording may be retained as a hidden benchmark.

## Release gates

No project dataset or data-derived artifact should be published until:

1. provenance, licence, consent, purpose, and intended users are documented and reviewed;
2. sensitive and prohibited content checks are complete;
3. access, retention, withdrawal, and deletion processes are operational;
4. representational gaps and foreseeable harms are published;
5. training/evaluation leakage and deduplication checks are documented;
6. evaluation scripts and hashes support reproduction without revealing participants; and
7. release has explicit maintainer approval following privacy and security review.

Until the upstream gaps and an independent evaluation are addressed, the selected model must remain labelled experimental and not approved for sensitive use.
