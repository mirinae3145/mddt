# Brief: microscopy data migration (project records)

Facts about a fictional university lab project. Use all of them; invent nothing that contradicts them.

## Project

- Goal: move about 180 TB of raw microscopy images from the lab's on-premises NAS to the campus object storage (S3-compatible) by the end of the semester, while keeping the analysis pipelines working.
- A second workstream drafts a data retention policy with campus IT.
- People: the lab manager owns the project; two PhD students run the analysis pipelines; a postdoc leads the retention policy; campus IT provides the storage and a contact for the policy.

## Status on 2026-11-10

- 95 TB migrated: all raw data from 2021 and 2022 (62 TB), and 33 TB of the 70 TB from 2023. The 2024 data (about 48 TB) is still on the NAS.
- Checksum verification passes for all migrated data.
- s3fs benchmark on the 2024 dataset: about 220 MB/s for sequential reads, but about 15 MB/s for random reads of small files. The segmentation pipeline, which reads many small files, is slowed down; the other pipelines are not.
- The NAS warranty expires in three and a half months.
- Retention policy: draft v0.2 is with campus IT for review.

## Storage layout

- Raw data goes to the bucket `lab-raw`, organized as `YEAR/PROJECT/ACQUISITION/`.
- Derived data goes to the bucket `lab-derived`, organized as `PROJECT/PIPELINE/RUN/`.
- Versioning is enabled on `lab-raw`, so an overwritten object keeps its earlier version.
- `lab-raw` uses object lock in governance mode for ten years. Governance mode lets a privileged role delete an object, which matches the approval rule in the retention policy.
- The NAS is a 12-bay unit with 220 TB of usable space.

## Batch procedure

- Data moves in batches of one project at a time.
- Each batch follows the same steps: take a read-only snapshot of the project on the NAS; bundle small files into tar archives (2023 data onward); copy with `rclone copy --checksum`; compare both sides with `rclone check`; update the inventory; mark the batch done.
- When `rclone check` reports a checksum mismatch, the batch is copied again, at most twice; after that the lab manager decides what to do.
- Bandwidth is limited to 800 MB/s between 07:00 and 22:00 and unlimited at night.

## Inventory

- A shared spreadsheet lists every project with its year, size, batch status, and the date it was verified.
- The inventory holds 214 projects; 131 are migrated as of 2026-11-10.

## Access

- Two storage roles exist: `pipeline-read`, which can only read, and `migration-write`, which can write to `lab-raw` and delete only objects it created within the last 24 hours.
- The two PhD students hold `migration-write`; the pipelines run with `pipeline-read`.
- Collaborators receive presigned download links that expire after seven days.

## Pipelines

- Three pipelines read the migrated data: segmentation, tracking, and deconvolution.
- Segmentation is slowed by small-file reads, as the benchmark showed.
- Tracking and deconvolution run at their earlier speed; deconvolution writes its results to `lab-derived`.

## Costs

- At full migration, storage is estimated at about 2,100 USD per month.
- The first monthly cost report, for October, came to 640 USD.

## Incidents

- 2026-10-08: a batch was copied twice because of a wrong destination path. The inventory check caught it, and the duplicate copy was deleted within 24 hours using `migration-write`.
- 2026-11-06: the s3fs mount dropped during a tracking run, and the run had to be restarted.
- 2026-11-09: an automatic remount of the s3fs mount was put in place.

## Communication

- A status email goes to the whole lab every Monday.
- Requests to campus IT go through its ticket system.

## Decisions

- 2026-09-12: transfer with rclone and checksum verification. Alternatives: `aws s3 sync` (no checksum check for multipart uploads) and a custom script (maintenance burden). Reconsider if the transfer rate stays below 1 TB per day.
- 2026-09-30: keep raw data in the standard tier and move derived data to the infrequent-access tier after 90 days. Alternatives: everything in standard (cost) and everything in infrequent access (retrieval cost for pipelines). Reconsider when quarterly cost reports arrive.
- 2026-10-14: the pipelines read through an s3fs mount instead of being rewritten for boto3. The alternative, a boto3 rewrite, would take about two weeks. Reconsider if s3fs throughput blocks analysis.
- 2026-10-24: from the 2023 data on, small files are bundled into one tar archive per acquisition before upload. Alternatives: keep individual files (slow uploads and listing) and zip archives (cannot be streamed). Reconsider if a pipeline needs random access inside bundles.
- 2026-11-03: keep the NAS as a read-only mirror for six months after the warranty ends, under an extended support contract that campus IT arranged. Alternatives: decommission the NAS at warranty end (no fallback) and buy a new NAS (cost). Reconsider if the support contract cannot be renewed.
- 2026-10-10: limit bandwidth to 800 MB/s during the day and leave it unlimited at night. Alternatives: always unlimited (slowed the network for other campus users) and a fixed lower limit (slower migration). Reconsider if the campus network policy changes.
- 2026-11-07: egress costs when collaborators download data are charged to the requesting group through its cost-center code. Alternative: the lab pays up to a yearly cap. Reconsider if collaborators object.

## Events

- 2026-09-05 kickoff.
- 2026-09-12 rclone chosen.
- 2026-09-20 5 TB pilot; three corrupt files found on the NAS and restored from tape.
- 2026-09-30 storage tiers decided.
- 2026-10-03 bulk transfer started, averaging 1.8 TB per day.
- 2026-10-08 duplicate batch caught by the inventory check and removed.
- 2026-10-10 bandwidth limit decided.
- 2026-10-14 s3fs decision.
- 2026-10-20 retention policy draft v0.1 reviewed with campus IT.
- 2026-10-21 transfer paused for two days during campus network maintenance.
- 2026-10-24 bundling decision.
- 2026-10-28 62 TB done; 2021 and 2022 complete.
- 2026-10-30 transfer rate dropped to 0.9 TB per day because of campus network throttling.
- 2026-11-01 campus IT raised the lab's network quality-of-service limit; the rate returned to about 1.8 TB per day.
- 2026-11-03 NAS mirror decision.
- 2026-11-05 s3fs benchmark completed.
- 2026-11-06 s3fs mount dropped during a tracking run.
- 2026-11-07 egress cost decision.
- 2026-11-09 automatic remount in place.
- 2026-11-10 retention policy draft v0.2 sent to campus IT; 95 TB done.

## Retention policy

- The funder requires raw data to be kept for ten years.
- The lab wants derived data kept for three years.
- Some datasets come from patient-derived samples and need access limited to approved lab members.
- Deleting raw data before the ten years end needs approval from the lab manager and campus IT.
- Still open in the draft: who approves deleting derived data, and how approvals are recorded.

## Meetings

- 2026-10-20, retention review (lab manager, postdoc, campus IT contact): agreed on the ten-year rule and access control for patient-derived data; asked the postdoc for a v0.2 with deletion approvals.
- 2026-11-07, cost review (lab manager, campus IT contact): agreed on charging egress to requesting groups; asked campus IT for monthly cost reports instead of quarterly ones.

## Risks

- The warranty may end before the 2024 data is migrated.
- Small-file performance may keep slowing the segmentation pipeline.
- Access control for patient-derived data must be in place before those datasets are migrated.
- Retrieval from the infrequent-access tier may cost more than estimated if derived data is reused often.
- A misconfigured object lock could block deletions that the retention policy allows.
- Only one PhD student currently runs the batches, so the migration depends on one person.

## Open questions

- How long to keep the tape backups after migration.
- Whether to re-verify checksums of the old tapes.
- Who approves deleting derived data.
- Whether derived data also needs object lock.

## Next actions

- Migrate the rest of the 2023 data (37 TB) by 2026-11-20 (PhD students).
- Migrate the 2024 data (about 48 TB) by 2027-01-31 (PhD students).
- Test bundled access for the segmentation pipeline by 2026-11-24 (PhD students).
- Finalize the retention policy with campus IT by 2026-12-15 (postdoc).
- Train the second PhD student on the batch procedure by 2026-11-17 (lab manager).

Deliverables: a records folder whose entry document is `README.md`, organized as the skill describes for project records. Keep only the kinds of records this material calls for, and decide how many files the content needs.
