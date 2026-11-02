# Command reference

This document is the reference for pixtwin's commands, the options of `report`, `move`, and `undo`, the exit codes, and logging.
Configuration options are in [configuration](configuration.md).

## Commands

pixtwin has these commands:

| Command | What it does |
| --- | --- |
| `pixtwin scan PATH` | Builds or updates the index for PATH |
| `pixtwin report` | Lists duplicate groups |
| `pixtwin move --to DIR` | Moves all but the kept photo of each group to DIR |
| `pixtwin undo` | Restores a move |
| `pixtwin verify` | Checks that the index matches the files on disk; new in 2.0 |
| `pixtwin prune` | Removes index entries for files that no longer exist |
| `pixtwin migrate` | Converts a 1.x index to the 2.0 format |

The `--profile NAME` option selects a [configuration profile](configuration.md#profiles).

## Report

`pixtwin report` prints a table by default.
The following options change its output and its filtering:

- **`--json`**: Prints JSON.
- **`--csv`**: Prints CSV.
- **`--only exact`** or **`--only near`**: Limits the kind of match.
- **`--min-size BYTES`**: Ignores smaller files.
- **`--group-size N`**: Shows only groups with at least N photos.

## Move

`pixtwin move --to DIR` moves all but the kept photo of each group to DIR.
Which photo is kept follows [these rules](kept-photo.md).
Without `--to`, `move` needs the `review_dir` option to be set.
`--dry-run` prints the plan without moving anything.
The layout of DIR is described in [the review folder](review-folder.md).

## Undo

`pixtwin undo` restores the last move.
Undo refuses to restore a file that was modified after the move, and reports which files it skipped.

- **`--list`**: Shows the last ten moves.
- **`--id N`**: Restores move N from that list.

## Exit codes

pixtwin exits with one of these codes:

| Code | Meaning |
| --- | --- |
| 0 | Success with no duplicates found |
| 1 | Duplicates found (for `report`) |
| 2 | Usage error |
| 3 | The index is locked by another pixtwin process |
| 4 | The index is from 1.x and needs `pixtwin migrate` |
| 5 | A permission error stopped `move` partway |

After exit code 5, the photos already moved are recorded, and `pixtwin undo` restores them.

## Logging

By default, pixtwin writes logs to `~/.cache/pixtwin/logs/`, rotated at 10 MB with five files kept.

- **`--verbose`**: Prints each file as it is processed.
- **`--log-file PATH`**: Writes the same output to a file, in place of the default log folder.
