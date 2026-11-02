# Batch procedure

This procedure moves one project from the lab's NAS to the object storage and records it as migrated.
Data moves one project at a time, and every batch follows the same steps.
It also covers what to do when a check fails and when copying may run at full speed.

## Steps

1. Take a read-only snapshot of the project on the NAS.
1. For data from 2023 onward, bundle small files into one tar archive per acquisition (see the [decision of 2026-10-24](decisions.md#2026-10-24-bundle-small-files-into-tar-archives)).
1. Copy the project with `rclone copy --checksum`.
1. Compare both sides with `rclone check`.
1. Update the inventory.
1. Mark the batch done.

The batch needs the `migration-write` role described in [storage layout and access](storage-and-access.md#storage-roles).
The inventory is the spreadsheet described in [migration status](status.md#inventory).

## When a check fails

When `rclone check` reports a checksum mismatch, copy the batch again.
Repeat the copy at most twice; after that, the lab manager decides what to do.

## Bandwidth limit

Copying is limited to 800 MB/s between 07:00 and 22:00 and is unlimited at night.
The reasons are in the [decision of 2026-10-10](decisions.md#2026-10-10-bandwidth-limit).
