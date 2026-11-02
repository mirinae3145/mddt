# pixtwin

pixtwin is a command-line tool that finds duplicate and near-duplicate photos in a library and moves the extra copies to a review folder.
It never deletes files.
It is for photographers and families with large photo libraries on local disks or a NAS.
This document covers installation, a first run, the tool's limits and privacy, and where the rest of the documentation is.

This is version 2.0, which changes the index format and some configuration keys compared with 1.x.
If you are upgrading, start with [migrating from 1.x](docs/migrating-from-1x.md).

## Installation

pixtwin requires Python 3.10 or later.
Install it with pipx:

```console
pipx install pixtwin
```

HEIC support needs the optional `libheif` library.
On Windows, HEIC files are skipped.

- **macOS**: Run `brew install libheif`.
- **Debian and Ubuntu**: Run `apt install libheif1`.

On a machine without internet access, download the wheel file from the releases page and install it from disk:

```console
pipx install ./pixtwin-2.0.0-py3-none-any.whl
```

## Quick start

A first run scans a folder, looks at the duplicate groups, and previews the move before anything changes.

1. Run `pixtwin scan PATH` to build the index for your photo folder.
1. Run `pixtwin report` to list the duplicate groups.
1. Run `pixtwin move --to DIR --dry-run` to print the plan without moving anything.
1. Run `pixtwin move --to DIR` to move the extra copies to the review folder `DIR`.
1. Run `pixtwin undo` if you want the last move reversed.

The [command reference](docs/cli.md) describes every command and option.

## Limitations

pixtwin does not handle every kind of file.

- RAW formats are not supported.
- Videos are ignored.
- Live Photos pairs are treated as two separate files.
- Scans of network shares are slow, as explained in [troubleshooting](docs/troubleshooting.md).

## Privacy

pixtwin makes no network connections.
Its index stores file paths, sizes, modification times, hashes, and a few EXIF fields, and no image data.
The [matching explanation](docs/matching.md#what-is-read-from-metadata) names the EXIF fields.

## More documentation

The documentation in [docs/](docs/README.md) is divided into guides, reference, and explanation, and its index says which document answers which question.
Contributors should read [CONTRIBUTING.md](CONTRIBUTING.md) for the source layout, checks, and pull request rules.
pixtwin is released under the MIT license.
