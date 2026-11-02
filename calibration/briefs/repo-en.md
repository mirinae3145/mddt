# Brief: pixtwin 2.0 (repository documentation)

Facts about a fictional open-source command-line tool. Use all of them; invent nothing that contradicts them.

## Product

- pixtwin finds duplicate and near-duplicate photos in a library and moves the extra copies to a review folder. It never deletes files.
- Intended users: photographers and families with large photo libraries on local disks or a NAS.
- This is version 2.0. It changes the index format and some configuration keys compared with 1.x.

## Installation

- Install with `pipx install pixtwin`. Requires Python 3.10 or later.
- HEIC support needs the optional `libheif` library: on macOS `brew install libheif`, on Debian and Ubuntu `apt install libheif1`. On Windows, HEIC files are skipped.
- For machines without internet access, a wheel file from the releases page can be installed with `pipx install ./pixtwin-2.0.0-py3-none-any.whl`.

## Commands

- `pixtwin scan PATH` builds or updates the index for PATH.
- `pixtwin report` lists duplicate groups. Output is a table by default, JSON with `--json`, and CSV with `--csv`.
- `report` filters: `--only exact` or `--only near` limits the kind of match; `--min-size BYTES` ignores smaller files; `--group-size N` shows only groups with at least N photos.
- `pixtwin move --to DIR` moves all but the kept photo of each group to DIR. `--dry-run` prints the plan without moving anything.
- `pixtwin undo` restores the last move by default. `pixtwin undo --list` shows the last ten moves, and `pixtwin undo --id N` restores one of them. Undo refuses to restore a file that was modified after the move, and reports which files it skipped.
- `pixtwin verify` (new in 2.0) checks that the index matches the files on disk.
- `pixtwin prune` removes index entries for files that no longer exist.
- `pixtwin migrate` converts a 1.x index to the 2.0 format.

## Which photo is kept

- By default, the photo with the highest resolution is kept.
- On a resolution tie, the photo with the oldest modification time is kept; on a further tie, the one with the shortest path.
- `--prefer PATH` makes photos under PATH win. It can be given several times; an earlier `--prefer` wins over a later one. Among preferred photos, the default rule still decides.
- When `respect_ratings = true`, a photo with an EXIF rating of 4 or 5 is kept over a higher-resolution photo without such a rating. This option is off by default.

## Matching

- Exact duplicates are found by SHA-256.
- Near-duplicates are found by a 64-bit difference hash (dHash) compared by Hamming distance, up to `threshold`.
- Burst shots, meaning photos from the same camera taken within 2 seconds of each other, are compared with `burst_threshold` instead of `threshold`.
- Rotated copies are detected by also hashing the 90, 180, and 270 degree rotations when `detect_rotation = true`. This adds about 30% to scan time.

## Configuration

- The configuration file is `~/.config/pixtwin/config.toml`.
- Options and defaults: `threshold` = 6; `burst_threshold` = 2; `detect_rotation` = true; `respect_ratings` = false; `index_path` = `~/.cache/pixtwin/index.sqlite`; `extensions` = jpg, jpeg, png, heic, tiff; `workers` = number of CPU cores; `follow_symlinks` = false; `review_dir` has no default, so `move` needs `--to` unless it is set.
- Profiles (new in 2.0): a `[profiles.NAME]` section overrides top-level options. Select a profile with `--profile NAME` or the environment variable `PIXTWIN_PROFILE`; the command-line option wins if both are given.
- A profile cannot change `index_path`, because all profiles share one index.

## Exit codes

- 0: success with no duplicates found; 1: duplicates found (for `report`); 2: usage error; 3: the index is locked by another pixtwin process; 4: the index is from 1.x and needs `pixtwin migrate`; 5: a permission error stopped `move` partway.
- After exit code 5, the photos already moved are recorded and `pixtwin undo` restores them.

## Migrating from 1.x

- Run `pixtwin migrate` once. It keeps the old index as `index.sqlite.v1`.
- Renamed configuration keys: `max_distance` became `threshold`, and `cache` became `index_path`. pixtwin 2.0 rejects the old names with an error that names the new key.
- The `--keep-newest` flag was removed; use `--prefer` with the folder that holds the newer copies.

## Troubleshooting

- Scans of network shares are slow because of latency rather than CPU; running pixtwin on the NAS itself, for example over SSH, is much faster.
- A warning that HEIC files were skipped means `libheif` is missing.
- "Index locked" means another scan is running. A lock file older than one hour is treated as stale and removed automatically.
- Burst shots grouped together wrongly call for a lower `burst_threshold`.

## Performance

- About 1,500 photos per minute on four cores reading from a hard disk, and about 4,000 per minute from an SSD.
- The first scan dominates; later scans only rehash files whose size or modification time changed.

## Design

- The pipeline has five stages: scan, hash, group, plan, and move. A rescan reuses the index from the earlier stages.
- The index is a SQLite database with tables for files, hashes, groups, and moves.
- Grouping uses a BK-tree over the hashes.
- Every move is written to a journal before it is carried out, which is what makes `undo` possible.

## Review folder

- `move` places each group's extra copies in `DIR/<group-id>/`, keeping each photo's path relative to the scanned root.
- Each move writes a `manifest.json` in DIR that lists every moved file, its original path, and its hash.
- Sidecar files with the same base name, such as `.xmp` and `.aae`, move together with their photo.
- A move across filesystems copies the file, verifies its hash, and only then removes the source.

## Metadata

- The EXIF orientation is applied before hashing, so a photo and its rotated-by-metadata copy match exactly.
- EXIF data is read for camera model, capture time (for burst detection), and rating; nothing else is stored.

## Multiple libraries

- Several roots can share one index, for example `pixtwin scan ~/Pictures /mnt/nas/photos`.
- Groups can span roots by default; `--within-root` limits groups to photos under the same root.
- A root that is temporarily unavailable, such as an unmounted NAS, is skipped with a warning and its index entries are kept.

## Python API

- The package exposes a `Library` class: `Library(index_path)`, `Library.scan(paths)`, `Library.groups(only=None)`, and `Library.plan(prefer=[])`, which returns the moves without performing them.
- The API is stable from 2.0 on and follows semantic versioning; anything not listed here is internal.

## Logging

- `--verbose` prints each file as it is processed; `--log-file PATH` writes the same output to a file.
- Without `--log-file`, logs go to `~/.cache/pixtwin/logs/`, rotated at 10 MB with five files kept.

## Scheduling

- A weekly cron job can run `pixtwin scan` followed by `pixtwin report --json`; because `report` exits with 1 when duplicates exist, the cron job can alert on that exit code.
- On Linux, a systemd timer works the same way; an example unit pair is `pixtwin-scan.service` and `pixtwin-scan.timer`.
- Scheduled runs never call `move`, so nothing changes without a person reviewing the report.

## Platform notes

- Windows: paths longer than 260 characters need long path support enabled in Windows.
- macOS: the Photos library package must not be scanned directly; export the photos first.
- Linux: scanning a NAS mounted over SMB works, but scanning on the NAS itself is faster.

## Privacy

- pixtwin makes no network connections.
- The index stores file paths, sizes, modification times, hashes, and the EXIF fields named above, and no image data.

## Release process (for maintainers)

- Releases are tagged `vMAJOR.MINOR.PATCH` on the main branch.
- CI runs the test suite on Python 3.10 to 3.13 on Linux, macOS, and Windows for every pull request.
- Pushing a release tag makes CI build the wheel and upload it to PyPI and to the releases page.
- The changelog entry for a release is written before the tag is pushed.

## Limitations

- RAW formats are not supported. Videos are ignored.
- Live Photos pairs are treated as two separate files.
- Network shares are slower, as described under troubleshooting.

## Contributing

- Source layout: `src/pixtwin` with the modules `cli`, `scan`, `hashing`, `grouping`, `planning`, and `index`.
- Tests run with pytest (`pytest -q`); linting uses ruff; type checking uses mypy, and CI enforces all three.
- Test fixtures are small synthetic images in `tests/photos`; never add personal photos.
- Every pull request includes tests and a changelog entry. Open an issue before proposing a new feature.
- Maintainers make releases.
- License: MIT. A changelog exists; do not write it.

Deliverables: `README.md`, `CONTRIBUTING.md`, and documents under `docs/`, organized as the skill describes. Decide how many documents the content needs.
