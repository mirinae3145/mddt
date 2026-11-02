# Report

This document describes the report figure-check writes: where it goes, its sections in order, how findings are identified, and what each figure's table contains.
It applies when compiling the report in the last step of the [workflow](workflow.md).

## Location

The report is written to `figure-check-report.md` next to the manuscript unless the user names another location.

## Sections

The report has these sections in this order:

1. A summary that counts findings by severity.
1. An "Across figures" section for issues that concern several figures at once, such as inconsistent fonts.
   Each such issue is reported there once.
1. One section for each figure.
1. A section for the supplementary figures.

## Findings

Every finding has an identifier made of the figure number and a running number, such as F2-03.
Each figure's section holds a table with one row per finding and these columns:

- **Issue**: What is wrong.
- **Rule**: The rule the finding applies.
- **Severity**: One of the [severity levels](severity.md#levels), with the "needs author check" flag where it applies.
- **Location**: Where in the figure the issue is.

An example finding: Figure 2b, the y-axis label lacks units, must fix.
