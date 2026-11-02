# Configuration

This document is the reference for pixtwin's configuration file: its location, every option with its default, and profiles.
Command-line options are in the [command reference](cli.md).

## Configuration file

pixtwin reads `~/.config/pixtwin/config.toml`.
The 2.0 release renamed two keys, as listed in [migrating from 1.x](migrating-from-1x.md).

## Options

The following table lists every option with its default and effect:

| Option | Default | Effect |
| --- | --- | --- |
| `threshold` | 6 | Largest Hamming distance at which photos count as near-duplicates |
| `burst_threshold` | 2 | The same limit, applied to burst shots |
| `detect_rotation` | true | Also detects rotated copies; adds about 30% to scan time |
| `respect_ratings` | false | Keeps a photo with an EXIF rating of 4 or 5 over a higher-resolution photo without one |
| `index_path` | `~/.cache/pixtwin/index.sqlite` | Where the index is stored |
| `extensions` | jpg, jpeg, png, heic, tiff | File types that are scanned |
| `workers` | number of CPU cores | Number of parallel workers |
| `follow_symlinks` | false | Whether scans follow symbolic links |
| `review_dir` | none | Default review folder for `move`; without it, `move` needs `--to` |

How the thresholds and rotation detection work is explained in [how matching works](matching.md).
`respect_ratings` is described with the other [keep rules](kept-photo.md).

## Profiles

A `[profiles.NAME]` section overrides the top-level options; profiles are new in 2.0.
Select a profile with `--profile NAME` or the environment variable `PIXTWIN_PROFILE`.
If both are given, the command-line option wins.

A profile cannot change `index_path`, because all profiles share one index.
