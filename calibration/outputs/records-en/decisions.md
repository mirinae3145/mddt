# Decisions

This document records the seven decisions that shaped the migration, in date order.
Each decision states the choice and its reason, compares the alternatives that were rejected, and names the condition for reconsidering it.

## 2026-09-12: Transfer with rclone

Data is transferred with rclone and checksum verification, as used in the [batch procedure](batch-procedure.md).

The alternatives were these:

| Alternative | Why it was rejected |
| --- | --- |
| `aws s3 sync` | It does not check checksums for multipart uploads. |
| A custom script | It would be a maintenance burden. |

Reconsider if the transfer rate stays below 1 TB per day.

## 2026-09-30: Storage tiers

Raw data stays in the standard tier, and derived data moves to the infrequent-access tier after 90 days.

The alternatives were these:

| Alternative | Why it was rejected |
| --- | --- |
| Everything in standard | The cost. |
| Everything in infrequent access | The retrieval cost for the pipelines. |

Reconsider when quarterly cost reports arrive.
The cost review of 2026-11-07 asked for monthly reports instead, so real tier costs will show up sooner; see [events and incidents](history.md#meetings).

## 2026-10-10: Bandwidth limit

Copying is limited to 800 MB/s during the day and unlimited at night.

The alternatives were these:

| Alternative | Why it was rejected |
| --- | --- |
| Always unlimited | It slowed the network for other campus users. |
| A fixed lower limit | The migration would be slower. |

Reconsider if the campus network policy changes.

## 2026-10-14: Read through an s3fs mount

The pipelines read through an s3fs mount instead of being rewritten for boto3.

The alternative was a boto3 rewrite, which would take about two weeks.

Reconsider if s3fs throughput blocks analysis.
The benchmark in [migration status](status.md#pipelines) shows the segmentation pipeline slowed by small-file reads, so this condition is being watched.

## 2026-10-24: Bundle small files into tar archives

From the 2023 data on, small files are bundled into one tar archive per acquisition before upload.

The alternatives were these:

| Alternative | Why it was rejected |
| --- | --- |
| Keeping individual files | Uploads and listing are slow. |
| Zip archives | They cannot be streamed. |

Reconsider if a pipeline needs random access inside bundles.
The segmentation test in the [plan](plan.md#next-actions) checks exactly this.

## 2026-11-03: Keep the NAS as a read-only mirror

The NAS stays as a read-only mirror for six months after the warranty ends, under an extended support contract that campus IT arranged.

The alternatives were these:

| Alternative | Why it was rejected |
| --- | --- |
| Decommissioning the NAS at warranty end | There would be no fallback. |
| Buying a new NAS | The cost. |

Reconsider if the support contract cannot be renewed.

## 2026-11-07: Egress costs

Egress costs of collaborator downloads are charged to the requesting group through its cost-center code.

The alternative was for the lab to pay up to a yearly cap.

Reconsider if collaborators object.
The download links themselves are described in [storage layout and access](storage-and-access.md#collaborator-downloads).
