---
name: figure-check
description: >
  Review the figures (plots, micrographs, photographs, diagrams) in a research
  manuscript draft before submission and write a report of issues with
  severities. Use when a user asks to check, review, or prepare the figures of
  a manuscript given as a PDF, DOCX, or LaTeX source. The skill reports issues
  and does not edit or redraw figures.
---

# figure-check

figure-check helps an agent review the figures in a research manuscript draft before submission and write a report of the issues it finds.
It checks plots, micrographs, photographs, and diagrams, and their captions and citations in the text, against general rules, rules for each figure type, and the target journal's author guidelines.
It reports issues and does not edit figures.
This file is the entry point; the procedure, rules, and report format live in the reference documents linked below.

## Scope

The skill covers the visual and descriptive quality of figures, including how captions and text refer to them.
The following are out of scope:

- The statistical validity of the analysis.
- Redrawing or otherwise editing figures.

## Procedure

Read [workflow](references/workflow.md) first, before starting a review.
It lists the required and optional inputs, what to settle with the user before starting, and the five steps from locating figures to compiling the report.

Two documents support the steps:

- [Reading the inputs](references/reading-inputs.md): how figures are read from a PDF, a DOCX file, or LaTeX source, and how font size in a raster figure is estimated.
  Read it when locating figures or measuring them.
- [Journal guidelines](references/journals.md): how the target journal's author guidelines override or relax the skill's rules, and which fields the skill reads from them.
  Read it when the user names a journal or supplies guidelines.

## Rules

Read [rules](references/rules.md) when checking figures.
It holds the rules that apply to every figure and introduces the rules for each figure type and for special cases, so read only the documents for the types present in the manuscript.

## Severity and report

Two documents govern the output:

- [Severity](references/severity.md): the three severity levels, the adjustments to them, and the "needs author check" flag.
  Read it when assigning a severity to a finding.
- [Report](references/report.md): the report's sections, finding identifiers, and per-figure tables.
  Read it when compiling the report in the last step.

## Background

Read these documents to understand the skill's boundaries and reasons, for example when a user asks what the skill cannot do.

- [Limitations](references/limitations.md): what the skill cannot establish from the inputs it has.
- [Rationale](references/rationale.md): why the skill checks figures this way.
