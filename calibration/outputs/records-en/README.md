# Microscopy data migration records

This folder holds the records of a lab project that moves about 180 TB of raw microscopy images from the lab's on-premises NAS to the campus object storage (S3-compatible) by the end of the semester, while keeping the analysis pipelines working.
It also covers a second workstream, a data retention policy drafted with campus IT.
The records are current as of 2026-11-10.

## People

The lab manager owns the project.
Two PhD students run the analysis pipelines and the migration batches.
A postdoc leads the retention policy.
Campus IT provides the storage and a contact for the policy.

## Communication

A status email goes to the whole lab every Monday.
Requests to campus IT go through its ticket system.

## Current state

These documents describe how things stand now, and they are rewritten as conditions change.

- [Migration status](status.md): progress by year, inventory counts, pipeline performance, and costs.
- [Storage layout and access](storage-and-access.md): the buckets, versioning and object lock, the NAS, the storage roles, and how collaborators download data.

## How the work is done

The [batch procedure](batch-procedure.md) gives the steps that move one project from the NAS to the object storage, what to do when a checksum check fails, and the bandwidth limit.

## Retention policy

The [retention policy](retention-policy.md) document covers the requirements behind the draft, its review state, and the points still open.

## History and reasons

These documents record what happened and why choices were made.

- [Events and incidents](history.md): dated events, incidents, and meetings from the kickoff to the present.
- [Decisions](decisions.md): seven decisions with their alternatives and the conditions for reconsidering each.

## Outlook

The [plan, risks, and open questions](plan.md) document lists next actions with owners and dates, known risks, and questions without an answer yet.
