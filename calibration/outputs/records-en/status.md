# Migration status

This document records the state of the migration on 2026-11-10: how much data has moved, how many projects are verified, how the pipelines perform on the object storage, and what it costs.
It is rewritten as conditions change, so it holds no history; see [events and incidents](history.md) for that.

## Progress

The migration has moved 95 TB of the roughly 180 TB of raw data, and checksum verification passes for all of it.
The data divides by acquisition year as follows:

| Year | Size | Migrated | State |
| --- | --- | --- | --- |
| 2021 and 2022 | 62 TB | 62 TB | Complete |
| 2023 | 70 TB | 33 TB | 37 TB remain on the NAS |
| 2024 | about 48 TB | none | On the NAS |

The NAS warranty expires in three and a half months, so the 2024 data is the pressing part; see [plan, risks, and open questions](plan.md) for the dates and the risk.

## Inventory

A shared spreadsheet lists every project with its year, size, batch status, and the date it was verified.
It holds 214 projects, and 131 of them are migrated as of 2026-11-10.
The [batch procedure](batch-procedure.md) updates it after each copy.

## Pipelines

Three pipelines read the migrated data through an s3fs mount, as chosen in the [decision of 2026-10-14](decisions.md#2026-10-14-read-through-an-s3fs-mount):

- **Segmentation**: Slowed down, because it reads many small files.
- **Tracking**: Runs at its earlier speed.
- **Deconvolution**: Runs at its earlier speed and writes its results to `lab-derived`.

The s3fs benchmark on the 2024 dataset explains the segmentation slowdown:

| Access pattern | Throughput |
| --- | --- |
| Sequential reads | about 220 MB/s |
| Random reads of small files | about 15 MB/s |

Bundling small files into tar archives is the planned remedy, and testing bundled access for segmentation is a next action in the [plan](plan.md#next-actions).

## Costs

Costs are tracked against an estimate for the full migration:

- **Estimate at full migration**: About 2,100 USD per month.
- **October report**: 640 USD, the first monthly cost report.
