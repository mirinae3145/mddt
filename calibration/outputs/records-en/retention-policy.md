# Retention policy

This document records the data retention policy that the lab is drafting with campus IT: the requirements behind it, its review state, and the points still open.
A postdoc leads the work, and campus IT provides a contact.

## Requirements

The draft rests on the following requirements:

- **Raw data**: The funder requires it to be kept for ten years.
- **Derived data**: The lab wants it kept for three years.
- **Patient-derived samples**: Some datasets come from such samples and need access limited to approved lab members.
- **Early deletion of raw data**: Deleting raw data before the ten years end needs approval from the lab manager and campus IT.

The ten-year rule and the approval rule are reflected in the object lock on `lab-raw`, described in [storage layout and access](storage-and-access.md#protection-of-raw-data).

## Review state

Draft v0.1 was reviewed with campus IT on 2026-10-20.
That meeting agreed on the ten-year rule and on access control for patient-derived data, and it asked the postdoc for a v0.2 with deletion approvals.
Draft v0.2 was sent to campus IT on 2026-11-10 and is with them for review.
The target date for finalizing the policy is in the [plan](plan.md#next-actions).

## Open points

Two points are still open in the draft:

- **Derived data**: Who approves deleting it.
- **Approvals**: How approvals are recorded.

Access control for patient-derived data must be in place before those datasets are migrated, as the [plan](plan.md#risks) notes.
