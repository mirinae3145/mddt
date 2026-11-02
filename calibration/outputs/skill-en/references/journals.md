# Journal guidelines

This document describes how figure-check uses the target journal's author guidelines, which fields it reads from them, and which requirement wins when the journal and the skill's rules differ.
It applies whenever the user names a journal or supplies its guidelines.

## Profile fields

A journal's author guidelines usually set these fields:

- **Font size**: The minimum font size.
- **Figure width**: The maximum figure width.
- **Color mode**: Color or grayscale printing.
- **File formats**: The accepted file formats.
- **Resolution**: The minimum resolution.

The skill reads these fields from the guidelines the user supplies and applies them in place of the defaults.
When the guidelines name accepted file formats, a figure in another format is a should-fix issue.

## Precedence

The journal's guidelines and the skill's rules are compared rule by rule.
The following table gives which requirement applies:

| Journal compared with the skill's rule | What applies |
| --- | --- |
| Stricter | The journal's requirement applies. |
| Silent | The skill's rule applies. |
| Looser | The skill's rule applies, reported as a suggestion. |

When the guidelines explicitly allow what a rule forbids, [severity](severity.md#adjustments) downgrades the finding to a suggestion.
