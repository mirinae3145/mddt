# Recognized conventions

Some documents follow a convention whose fixed structure the model accommodates, as [common uses](uses.md) describes.
This document says which conventions the checker recognizes, how it recognizes them, and which findings it omits for them.
Read it when writing or checking a changelog or a MADR decision record, or when such a file gets fewer findings than expected.

## Recognition

The checker recognizes the following conventions:

- **Changelogs**: Files whose names match `CHANGELOG` or `CHANGELOG.*`, without regard to case, including `CHANGELOG.md` and `changelog.en.md`.
  Directory searches still select only `.md` files; other matching names can be given explicitly.
- **MADR decision records**: Other files whose H2s include both "Context and Problem Statement" and "Decision Outcome", the mandatory sections of [MADR](https://adr.github.io/madr/).
  Their names and folders do not matter.
  Titles are compared without case, and whitespace and inline formatting do not affect matching.
  Translated templates are not recognized and keep the ordinary document rules.

Other files use the ordinary document rules.

## Omitted findings

The following findings are omitted for each convention:

| Scope | Changelogs | MADR decision records |
| --- | --- | --- |
| Overviews and heading form | `h1-overview`, `topic-overview`, `heading-depth`, `heading-number` | `h1-overview`, `topic-overview` |
| Topic organization | `part-after-topic`, `topic-single-child` | `part-after-topic`, `topic-single-child` |
| Counts and sizes | `list-single`, `list-length`, `section-count`, `sibling-imbalance`, `file-size` | `list-single` |
| List introductions | `list-intro`, and `heading-intro` for lists only | None |
| Links into the file, regardless of which file contains the link | `anchor-to-part` | `link-without-summary` |

All other findings remain applicable, including links from these files into ordinary documents.
In a changelog, a table directly under H1 or under a heading with subheadings still needs an introductory paragraph.
In a MADR record, a list or table directly under H1 or a topic H2 needs one, where the waived overview would have introduced it.
Outlines of changelogs show heading levels and list statistics without topic, part, or overview labels.
Outlines of MADR records keep topic and part labels without overview labels.
