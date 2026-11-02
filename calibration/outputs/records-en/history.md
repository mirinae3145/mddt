# Events and incidents

This document records, in date order, what happened in the migration and the retention policy work: events, incidents, and meetings.
The reasons behind choices are in [decisions](decisions.md), and the present state is in [migration status](status.md).

## Events

The events run from the kickoff to 2026-11-10:

- **2026-09-05**: Kickoff.
- **2026-09-12**: rclone chosen.
- **2026-09-20**: 5 TB pilot; three corrupt files found on the NAS and restored from tape.
- **2026-09-30**: Storage tiers decided.
- **2026-10-03**: Bulk transfer started, averaging 1.8 TB per day.
- **2026-10-08**: Duplicate batch caught by the inventory check and removed.
- **2026-10-10**: Bandwidth limit decided.
- **2026-10-14**: s3fs decision.
- **2026-10-20**: Retention policy draft v0.1 reviewed with campus IT.
- **2026-10-21**: Transfer paused for two days during campus network maintenance.
- **2026-10-24**: Bundling decision.
- **2026-10-28**: 62 TB done; 2021 and 2022 complete.
- **2026-10-30**: Transfer rate dropped to 0.9 TB per day because of campus network throttling.
- **2026-11-01**: Campus IT raised the lab's network quality-of-service limit; the rate returned to about 1.8 TB per day.
- **2026-11-03**: NAS mirror decision.
- **2026-11-05**: s3fs benchmark completed.
- **2026-11-06**: s3fs mount dropped during a tracking run.
- **2026-11-07**: Egress cost decision.
- **2026-11-09**: Automatic remount in place.
- **2026-11-10**: Retention policy draft v0.2 sent to campus IT; 95 TB done.

## Incidents

These incidents disturbed the work, and the last item is the response to the second:

- **2026-10-08**: A batch was copied twice because of a wrong destination path.
  The inventory check caught it, and the duplicate copy was deleted within 24 hours using `migration-write`.
- **2026-11-06**: The s3fs mount dropped during a tracking run, and the run had to be restarted.
- **2026-11-09**: An automatic remount of the s3fs mount was put in place, in response to the drop of 2026-11-06.

The role used for the deletion is described in [storage layout and access](storage-and-access.md#storage-roles).

## Meetings

Two meetings produced decisions and requests:

- **2026-10-20, retention review**: Attended by the lab manager, the postdoc, and the campus IT contact.
  They agreed on the ten-year rule and access control for patient-derived data, and asked the postdoc for a v0.2 with deletion approvals.
- **2026-11-07, cost review**: Attended by the lab manager and the campus IT contact.
  They agreed on charging egress to requesting groups, and asked campus IT for monthly cost reports instead of quarterly ones.
