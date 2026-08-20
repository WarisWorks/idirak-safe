# Idirak Safe

Idirak Safe is a proposed local-first, open-source Uyghur transcription tool for people handling sensitive human-rights documentation. The intended users include Uyghur-speaking advocates, journalists, researchers, archivists, and civil-society groups that need to turn recordings into reviewable text without uploading them to a hosted service.

> [!WARNING]
> **Pre-alpha scaffold:** this repository does not yet include a working ASR model or transcription backend. It cannot currently transcribe audio. Do not rely on it for investigations, testimony, emergencies, or other sensitive work.

Idirak Safe is a new, focused project. It is separate from the existing hosted services at [Idirak](https://www.idirak.com/); those services are not being represented here as open-source, offline, or appropriate for sensitive material.

## Why this project exists

Submitting recordings to a remote service can expose their content, metadata, speakers, or users. Idirak Safe is being designed around a simpler trust boundary: after software and an appropriately licensed model have been installed, transcription should be able to happen on a device controlled by the user.

The project follows these principles:

- **Local by default:** source media, intermediate data, and transcripts stay on the user's device.
- **No silent network fallback:** if a selected local backend is unavailable, the operation must fail clearly instead of sending data elsewhere.
- **No telemetry:** the core command-line application does not collect analytics or transmit usage data.
- **Minimal retention:** temporary files and logs should not contain transcript content unless the user explicitly requests it.
- **User-controlled outputs:** users choose where exported transcripts are written and when they are deleted.
- **Honest limitations:** accuracy, language coverage, model licensing, and security properties must be documented and tested rather than assumed.

Local processing reduces some risks, but it does not make a device safe. Idirak Safe does not provide disk encryption, endpoint protection, anonymity, malware protection, secure deletion guarantees, or legal advice.

## Current functionality

The initial scaffold is intentionally small. It currently provides:

- a `doctor` command that reports the project's pre-alpha, local-only status;
- a `transcribe` command that exits with a clear unimplemented-feature message rather than using a remote fallback;
- validation of a simple local transcript document;
- local export from transcript JSON to plain text, SRT, VTT, or normalized JSON;
- unit tests for the implemented behavior; and
- no network calls, telemetry, bundled model, or working ASR backend.

The following are **planned, not implemented**:

- local audio/media import;
- an explicitly selected, locally installed Uyghur ASR backend;
- offline inference and transcript generation;
- documented model provenance, licensing, checksums, and evaluation;
- privacy and security hardening suitable for cautious field testing; and
- packaging that can be installed without contacting a service at transcription time.

See [ROADMAP.md](ROADMAP.md) for the proposed six-month work plan and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the intended data flow.

## Install the scaffold

Requirements:

- Python 3.10 or newer
- Git

```bash
git clone https://github.com/WarisWorks/idirak-safe.git
cd idirak-safe
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

On Windows PowerShell, activate the environment with `.venv\\Scripts\\Activate.ps1` instead.

Check the current status:

```bash
idirak-safe doctor
```

Run the test suite:

```bash
python -m unittest discover -s tests -v
```

The runtime scaffold uses only the Python standard library. A future ASR backend will add separately documented dependencies and model requirements.

## Export an existing transcript

The current CLI accepts a local JSON transcript with a required, non-empty `segments` list. `language` defaults to `ug`; `source` and segment-level `speaker` values are optional.

```json
{
  "language": "ug",
  "source": "interview-01.wav",
  "segments": [
    {
      "start": 0.0,
      "end": 2.4,
      "text": "سالام دۇنيا"
    }
  ]
}
```

Export it locally:

```bash
idirak-safe export examples/sample_transcript.json \
  --format txt \
  --output transcript.txt
```

Supported export formats are `txt`, `srt`, `vtt`, and `json`. Existing output files are preserved unless `--force` is passed. This conversion does not perform speech recognition.

## Safe-use limitations

- Treat the repository as experimental software, not a production security tool.
- Do not test it with identifiable testimony or operationally sensitive recordings.
- Use synthetic, public-domain, or explicitly consented non-sensitive samples during development.
- Review model and dataset licences before downloading or redistributing them.
- Verify transcripts manually; speech recognition errors can change names, dates, quotations, and meaning.
- Protect the device, backups, swap space, shell history, and exported files using practices appropriate to the user's risk environment.
- Consider whether merely possessing a recording or transcript could endanger someone before creating either one.

Security and privacy concerns can be reported using the process in `SECURITY.md`. Please do not include sensitive recordings, transcripts, identities, or credentials in a public issue.

## Project links

- Repository: <https://github.com/WarisWorks/idirak-safe>
- Idirak: <https://www.idirak.com/>
- Developer portfolio: <https://warisruzi.com/>
- Developer profiles: <https://github.com/WarisWorks> and <https://github.com/WarisRuzi>

## Contributing

Contributions are welcome once the scope and safety boundaries are understood. See `CONTRIBUTING.md` before opening a pull request. Do not submit private recordings, personal data, confidential testimony, or unlicensed datasets.

## Licence

The source code in this repository is licensed under the [Apache License 2.0](LICENSE). Models, datasets, media samples, and third-party dependencies may have different licences; each must be documented separately before it is added or recommended.
