# The review folder

This document is the reference for what `pixtwin move --to DIR` writes: the folder layout, the manifest, the files that move together, and what happens across filesystems.
Which photo stays behind is covered in [which photo is kept](kept-photo.md).

## Layout

`move` places each group's extra copies in `DIR/<group-id>/`.
Each photo keeps its path relative to the scanned root.

## Manifest

Each move writes a `manifest.json` in DIR.
It lists every moved file, its original path, and its hash.

## Sidecar files

Sidecar files with the same base name, such as `.xmp` and `.aae`, move together with their photo.

## Moves across filesystems

When DIR is on another filesystem, `move` copies the file, verifies its hash, and only then removes the source.
