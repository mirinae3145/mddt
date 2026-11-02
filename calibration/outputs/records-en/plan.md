# Plan, risks, and open questions

This document looks ahead from 2026-11-10: the actions that are due, the risks that could disturb them, and the questions that have no answer yet.
It is rewritten as items are done, resolved, or added.

## Next actions

Five actions are open:

| Action | Due | Owner |
| --- | --- | --- |
| Train the second PhD student on the [batch procedure](batch-procedure.md) | 2026-11-17 | Lab manager |
| Migrate the rest of the 2023 data (37 TB) | 2026-11-20 | PhD students |
| Test bundled access for the segmentation pipeline | 2026-11-24 | PhD students |
| Finalize the [retention policy](retention-policy.md) with campus IT | 2026-12-15 | Postdoc |
| Migrate the 2024 data (about 48 TB) | 2027-01-31 | PhD students |

Testing bundled access answers the small-file slowdown in [migration status](status.md#pipelines).
The two migration actions follow from the [progress](status.md#progress) by year.

## Risks

These risks are known, and the list may be incomplete:

- **Warranty**: It may end before the 2024 data is migrated.
- **Small-file performance**: It may keep slowing the segmentation pipeline.
- **Patient-derived data**: Access control must be in place before those datasets are migrated.
- **Infrequent-access retrieval**: It may cost more than estimated if derived data is reused often.
- **Object lock**: A misconfigured lock could block deletions that the retention policy allows.
- **Single operator**: Only one PhD student currently runs the batches, so the migration depends on one person; the training action in [next actions](#next-actions) addresses this.

## Open questions

These questions have no answer yet:

- How long to keep the tape backups after migration.
- Whether to re-verify checksums of the old tapes.
- Who approves deleting derived data.
- Whether derived data also needs object lock.
