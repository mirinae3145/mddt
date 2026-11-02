# pixtwin documentation

This folder documents pixtwin 2.0 for people who use the tool, divided into guides for tasks, reference for exact facts, and explanation of how the tool works.
For installation and a first run, see the [README](../README.md).

## Guides

Each guide walks through one task:

- [Migrating from 1.x](migrating-from-1x.md): converting a 1.x index, renaming configuration keys, and replacing `--keep-newest`.
- [Running pixtwin unattended](unattended-runs.md): a weekly cron job or systemd timer that reports duplicates and alerts on them.
- [Troubleshooting](troubleshooting.md): causes and fixes for slow scans, skipped HEIC files, a locked index, and wrongly grouped burst shots.

## Reference

Reference documents state exact behavior and options:

- [Command reference](cli.md): every command, the `report` filters, undo, exit codes, and logging.
- [Configuration](configuration.md): the configuration file, every option and its default, and profiles.
- [Which photo is kept](kept-photo.md): the rules that choose the photo to keep in each group.
- [The review folder](review-folder.md): how `move` lays out the review folder and what it records.
- [Libraries, platforms, and performance](environments.md): scanning several roots, platform notes, and scan speed.
- [Python API](python-api.md): the stable `Library` class.

## Explanation

Explanation documents describe why the tool behaves as it does:

- [How matching works](matching.md): exact and near-duplicate detection, bursts, rotation, and the metadata that is read.
- [Design](design.md): the pipeline, the index, grouping, and the move journal that makes undo possible.
