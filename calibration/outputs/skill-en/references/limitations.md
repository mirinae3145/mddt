# Limitations

This document states what figure-check cannot establish from the inputs it has.
Read it to know which findings are estimates and which checks the skill does not perform.

## What the skill cannot establish

The skill has these limitations:

- **Raster font sizes**: Font sizes in raster figures are estimates, as [reading the inputs](reading-inputs.md#font-size-in-raster-figures) explains.
- **Uniform adjustment**: The skill cannot tell whether a contrast adjustment was uniform when only the final image is available.
  - It flags the figure for author check instead, as [severity](severity.md#needs-author-check) describes.
- **Source files**: The skill does not open figure source files such as spreadsheets or plotting scripts.
