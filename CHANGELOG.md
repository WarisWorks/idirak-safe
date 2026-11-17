# Changelog

Notable changes to Idirak Safe. The project is pre-alpha and does not yet promise a stable API or file format.

## Unreleased

### Fixed

- SRT and WebVTT exports no longer let transcript text create an extra cue: blank lines inside a segment are dropped and WebVTT output escapes `&`, `<`, and `>`.
- TXT export keeps one segment per line when segment text contains line breaks.
- A transcript JSON file with an oversized number or extreme nesting now produces a validation error instead of a traceback.
- Model verification reports a symbolic link consistently, independent of directory listing order.
- Writing a new output file works on filesystems without hard links, such as FAT or exFAT drives.

### Changed

- Transcripts and segments are validated when constructed in code, not only when parsed from JSON.
- Control characters are rejected in transcript fields, except tabs and line breaks in segment text.
- `export` reads at most 8 MiB and accepts a UTF-8 byte-order mark.
- `doctor` reports the package version, the pinned model revision, and whether the optional ASR packages can be found.
- The package version is defined once, in `idirak_safe.__version__`.

### Added

- `idirak-safe --version`.
- In-process network-policy regression tests.

## 0.2.0a0

- Experimental, checksum-pinned, offline-only local Uyghur ASR path for short strict PCM WAV input.
- Transcript validation and TXT, SRT, VTT, and JSON export.
