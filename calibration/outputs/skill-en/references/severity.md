# Severity

This document defines the severity levels figure-check assigns to findings, the adjustments applied to them, and the "needs author check" flag.
It applies in the last step of the [workflow](workflow.md), when findings are compiled into the [report](report.md).

## Levels

Every finding has one of three severities:

| Severity | Meaning |
| --- | --- |
| Must fix | The figure breaks a journal guideline, or the issue can change how the data is interpreted. |
| Should fix | The issue affects readability only. |
| Suggestion | The issue concerns stylistic consistency only. |

## Adjustments

These adjustments apply to the levels above:

- **Journal allows it**: When the journal guidelines explicitly allow what a rule forbids, the finding is downgraded to a suggestion.
- **Repeated findings**: Repeated findings of the same rule in one figure are reported once, with the number of occurrences.

## Needs author check

"Needs author check" is a flag added to a finding whose correctness the skill cannot establish, such as a borderline font size or an adjustment that may not be uniform.
The finding keeps its severity.
[Reading the inputs](reading-inputs.md#font-size-in-raster-figures) and [limitations](limitations.md) describe where the skill cannot establish a result.
