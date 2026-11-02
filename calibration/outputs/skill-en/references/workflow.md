# Review workflow

This document describes how an agent reviews the figures of a manuscript draft with figure-check, from the inputs it needs to the finished report.
It covers the inputs, what to settle before starting, and the five steps of the review.

## Inputs

The skill takes these inputs:

- **Required**: The manuscript as a PDF, a DOCX file, or LaTeX source.
- **Optional**: The separate figure files, and the target journal's author guidelines.

## Before starting

Settle these points with the user before the first step:

- **Journal**: If the user has not said which journal the manuscript targets, ask.
  - Without a journal, use the default print sizes given in step 2.
- **Report location**: The report is written to `figure-check-report.md` next to the manuscript unless the user names another location.

## Steps

Follow these steps in order:

1. Locate the figures.
   - In a PDF or DOCX file, find captions that start with "Figure N" or "Fig. N".
   - In LaTeX source, find `\includegraphics` inside figure environments.
   - Find supplementary figures ("Figure S1") the same way.
   See [reading the inputs](reading-inputs.md) for how each format is read.
1. Determine the print size of each figure.
   Use 85 mm wide for a single column and 180 mm for a double column, unless the journal guidelines say otherwise, as described in [journal guidelines](journals.md).
1. Check each figure against the [general rules](rules.md#general-rules) and the rules for its type, which [rules](rules.md#rules-by-figure-type) introduces.
1. Check each caption against its figure, and check the text.
   - For each caption, confirm that every panel is mentioned, abbreviations are defined, and units match.
   - For the text, confirm that every figure the text cites exists and that figures are first cited in numerical order.
1. Compile the report as described in [report](report.md), assigning severities with [severity](severity.md).
