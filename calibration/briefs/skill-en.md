# Brief: figure-check (agent skill)

Facts about a fictional agent skill. Use all of them; invent nothing that contradicts them.

## Purpose and scope

- figure-check helps an agent review the figures (plots, micrographs, diagrams) in a research manuscript draft before submission. It reports issues; it does not edit figures.
- Out of scope: the statistical validity of the analysis, and redrawing figures.

## Inputs

- Required: the manuscript as a PDF, a DOCX file, or LaTeX source.
- Optional: the separate figure files, and the target journal's author guidelines.

## Before starting

- Ask which journal the manuscript targets if the user has not said; without a journal, use the default print sizes.
- The report is written to `figure-check-report.md` next to the manuscript unless the user names another location.

## Workflow

- Step 1, locate figures: in a PDF or DOCX, find captions that start with "Figure N" or "Fig. N"; in LaTeX, find `\includegraphics` inside figure environments. Supplementary figures ("Figure S1") are found the same way.
- Step 2, determine the print size: 85 mm wide for a single column and 180 mm for a double column, unless the journal guidelines say otherwise.
- Step 3, check each figure against the general rules and the rules for its type.
- Step 4, check each caption against its figure: every panel is mentioned, abbreviations are defined, and units match.
- Step 4 also checks the text: every figure the text cites exists, and figures are first cited in numerical order.
- Step 5, compile the report.

## General rules

- Text in figures is at least 6 pt at final print size.
- Fonts are consistent across figures.
- Panels are labeled (a, b, c) consistently, and the caption refers to each panel.
- Color schemes stay readable for color-blind readers and never rely on red-green contrast alone. When the journal prints in grayscale, the figure must also work in grayscale.
- Raster images are at least 300 dpi at print size.

## Reading the inputs

- In a DOCX file, figures are embedded images; the skill reads them at their embedded resolution.
- In a PDF, vector figures are checked at any zoom, while raster figures are checked at their pixel size.
- In LaTeX, `subfigure` and `subcaption` environments count as panels of one figure.
- Font size in a raster figure is estimated from the pixel height of capital letters at the print width, so a borderline result is reported as "needs author check" rather than as a definite issue.

## Rules for multi-panel figures

- Panels are aligned on a common grid.
- Panels that are meant to be compared share axis ranges, or the caption says that they do not.
- Units are consistent across panels.
- A figure that combines panel types, such as a micrograph next to a plot, gets each type's rules per panel.

## Rules for plots

- Axes carry labels with units, and logarithmic scales are marked as such.
- Legends do not cover data.
- Error bars are defined in the caption (SD or SEM, and n).
- Significance markers such as asterisks are defined with their p thresholds.
- Axes are not truncated without break marks.
- Bar charts start at zero.
- Continuous data uses a perceptually uniform color map; rainbow maps such as jet are a should-fix issue.
- The caption states n for each group shown.
- Pie charts with more than five slices get a suggestion to use a bar chart.

## Rules for micrographs

- Micrographs have scale bars with a stated length; a magnification value does not replace a scale bar.
- Contrast and brightness adjustments are applied to the whole image and disclosed in the methods or caption.
- Pseudo-color is described in the caption.
- Insets are marked on the parent image with a box.

## Rules for photographs

- Photographs other than micrographs, such as field or specimen photos, include a scale reference when size matters.
- A photograph showing an identifiable person needs a consent statement in the caption or methods; a missing statement is a must-fix issue.

## Rules for diagrams

- Arrows and symbols are explained in a legend or the caption.
- Line styles and shapes are used consistently within the diagram.

## Severity

- Must fix: the figure breaks a journal guideline, or the issue can change how the data is interpreted.
- Should fix: the issue affects readability only.
- Suggestion: the issue concerns stylistic consistency only.
- When the journal guidelines explicitly allow what a rule forbids, the finding is downgraded to a suggestion.
- Repeated findings of the same rule in one figure are reported once, with the number of occurrences.
- "Needs author check" is a flag added to a finding whose correctness the skill cannot establish, such as a borderline font size or an adjustment that may not be uniform; the finding keeps its severity.

## Journal guidelines

- When the journal is stricter than a rule, the journal's requirement applies.
- When the journal is silent, the skill's rule applies.
- When the journal is looser, the skill's rule is reported as a suggestion.

## Journal profiles

- A journal's author guidelines usually set a minimum font size, maximum figure width, color mode, accepted file formats, and minimum resolution.
- The skill reads these fields from the guidelines the user supplies and applies them in place of the defaults.
- When the guidelines name accepted file formats, a figure in another format is a should-fix issue.

## Special cases

- Gel and blot images: splicing lanes without marking the splice is a must-fix integrity issue.
- Figures reused from an earlier publication need a permission note in the caption; a missing note is a should-fix issue.
- Supplementary figures are checked with the same rules but reported in a separate section.

## Report

- The report starts with a summary that counts findings by severity.
- After the summary comes an "Across figures" section for issues that concern several figures at once, such as inconsistent fonts; each such issue is reported there once.
- Then each figure gets its own section, followed by the supplementary figures.
- Every finding has an identifier made of the figure number and a running number, such as F2-03.
- Each figure gets a table with the issue, the rule, the severity, and the location in the figure.
- Example finding: Figure 2b, the y-axis label lacks units, must fix.

## Limitations

- Font sizes in raster figures are estimates.
- The skill cannot tell whether a contrast adjustment was uniform when only the final image is available; it flags the figure for author check instead.
- The skill does not open figure source files such as spreadsheets or plotting scripts.

## Rationale

- Reviewers reject unclear figures.
- Color-blind readers are about one in twelve men.
- Journals and institutions have integrity rules on image manipulation.

Deliverables: `SKILL.md` with a `name` and `description` in its frontmatter, and documents under `references/`, organized as the skill describes. Decide how many documents the content needs.
