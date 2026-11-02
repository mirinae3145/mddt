# Troubleshooting

This guide lists common problems with pixtwin, their causes, and what to do about each.
For an unexpected exit code, see the [exit codes](cli.md#exit-codes).

| Symptom | Cause | Fix |
| --- | --- | --- |
| Scans of a network share are slow | Latency, not CPU, is the limit | Run pixtwin on the NAS itself, for example over SSH, which is much faster |
| A warning says HEIC files were skipped | The `libheif` library is missing | Install `libheif` as described in the [README](../README.md#installation) |
| "Index locked" | Another scan is running | Wait for it to finish; a lock file older than one hour is treated as stale and removed automatically |
| Burst shots are grouped together wrongly | `burst_threshold` is too high | Lower `burst_threshold` in the [configuration](configuration.md#options) |

On Windows, HEIC files are always skipped, so the HEIC warning there is expected.
