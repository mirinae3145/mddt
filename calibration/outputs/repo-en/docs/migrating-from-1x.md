# Migrating from 1.x

This guide upgrades a pixtwin 1.x setup to 2.0, which changes the index format and some configuration keys.
It covers converting the index, renaming configuration keys, and replacing a removed flag.

With a 1.x index, pixtwin 2.0 stops with exit code 4 until the index is converted.

1. Run `pixtwin migrate` once.
   It converts the 1.x index to the 2.0 format and keeps the old index as `index.sqlite.v1`.
1. Rename the configuration keys in `~/.config/pixtwin/config.toml`:
   - `max_distance` becomes `threshold`.
   - `cache` becomes `index_path`.
1. Replace every use of `--keep-newest` with `--prefer` and the folder that holds the newer copies.

pixtwin 2.0 rejects the old key names with an error that names the new key, so a missed rename is easy to find.
The `--keep-newest` flag was removed, so scripts that still use it fail.
See [which photo is kept](kept-photo.md) for how `--prefer` works.
