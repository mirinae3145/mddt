# Reading the inputs

This document states how figure-check reads figures from each input format and how it estimates font size in raster figures.
It applies to locating figures in the first step of the [workflow](workflow.md) and to measuring them in the third.

## Formats

The skill reads each format as follows:

| Format | How figures are read |
| --- | --- |
| DOCX | Figures are embedded images, and the skill reads them at their embedded resolution. |
| PDF, vector figure | The figure is checked at any zoom. |
| PDF, raster figure | The figure is checked at its pixel size. |
| LaTeX | `subfigure` and `subcaption` environments count as panels of one figure. |

## Font size in raster figures

The skill estimates font size in a raster figure from the pixel height of capital letters at the print width.
Because this is an estimate, a borderline result is reported as "needs author check" rather than as a definite issue, as [severity](severity.md#needs-author-check) describes.
[Limitations](limitations.md) lists the other estimates the skill makes.
