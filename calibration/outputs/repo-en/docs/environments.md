# Libraries, platforms, and performance

This document is the reference for running pixtwin on different libraries and systems: scanning several roots, notes for Windows, macOS, and Linux, and scan speed.

## Multiple libraries

Several roots can share one index, for example:

```console
pixtwin scan ~/Pictures /mnt/nas/photos
```

By default, groups can span roots.
`--within-root` limits groups to photos under the same root.
A root that is temporarily unavailable, such as an unmounted NAS, is skipped with a warning, and its index entries are kept.

## Platform notes

Each platform has one thing to watch:

- **Windows**: Paths longer than 260 characters need long path support enabled in Windows.
- **macOS**: Do not scan the Photos library package directly; export the photos first.
- **Linux**: Scanning a NAS mounted over SMB works, but scanning on the NAS itself is faster.

## Performance

pixtwin scans about 1,500 photos per minute on four cores reading from a hard disk, and about 4,000 per minute from an SSD.
The first scan dominates, because later scans only rehash files whose size or modification time changed.
Enabling `detect_rotation` adds about 30% to scan time.
