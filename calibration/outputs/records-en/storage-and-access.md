# Storage layout and access

This document describes how data is organized in the campus object storage, what protects it, which roles may touch it, and how collaborators get copies.
It also records the capacity of the NAS that the data is leaving.

## Buckets

The storage has two buckets, one for each kind of data:

- **`lab-raw`**: Raw data, organized as `YEAR/PROJECT/ACQUISITION/`.
- **`lab-derived`**: Derived data, organized as `PROJECT/PIPELINE/RUN/`.

The tiers of each bucket follow the [decision of 2026-09-30](decisions.md#2026-09-30-storage-tiers).

## Protection of raw data

Two settings protect `lab-raw`:

- **Versioning**: It is enabled, so an overwritten object keeps its earlier version.
- **Object lock**: It runs in governance mode for ten years.
  - Governance mode lets a privileged role delete an object, which matches the approval rule in the [retention policy](retention-policy.md).

## Storage roles

Two roles exist, and each has a fixed set of holders:

| Role | Permissions | Held by |
| --- | --- | --- |
| `pipeline-read` | Read only | The pipelines |
| `migration-write` | Write to `lab-raw`; delete only objects it created within the last 24 hours | The two PhD students |

The 24-hour deletion window is what removed the duplicate batch of 2026-10-08, as told in [events and incidents](history.md#incidents).

## Collaborator downloads

Collaborators receive presigned download links that expire after seven days.
The egress costs of those downloads follow the [decision of 2026-11-07](decisions.md#2026-11-07-egress-costs).

## The NAS

The NAS is a 12-bay unit with 220 TB of usable space.
Its warranty and its planned afterlife are covered in [migration status](status.md#progress) and the [decision of 2026-11-03](decisions.md#2026-11-03-keep-the-nas-as-a-read-only-mirror).
