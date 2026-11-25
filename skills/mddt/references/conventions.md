# Recognized conventions

Some documents follow a convention whose fixed structure the model accommodates, as [common uses](uses.md) describes.
This document says which conventions the checker recognizes, how it recognizes them, and which findings it omits for them.
Read it when writing or checking a changelog or a MADR decision record, or when such a file gets fewer findings than expected.

## Recognition

The checker recognizes the following conventions:

- **Changelogs**: Files whose names match `CHANGELOG` or `CHANGELOG.*`, without regard to case, including `CHANGELOG.md` and `changelog.en.md`.
  Directory searches still select only `.md` files; other matching names can be given explicitly.
- **MADR decision records**: Other files whose H2s include both "Context and Problem Statement" and "Decision Outcome", two sections that every [MADR](https://adr.github.io/madr/) template requires.
  Their names and folders do not matter.
  Titles are compared without case, and whitespace and inline formatting do not affect matching.

The outline of a recognized file names its convention, so a file without that line was not recognized.
Outlines of changelogs show heading levels and list statistics without topic, part, or overview labels.
Outlines of MADR records keep topic and part labels and omit overview labels for the template's sections.

Other files use the ordinary document rules.
Records with translated section titles, and drafts that lack one of the two sections, are such files.
Their findings are a conflict between the template and the model, which [combining mddt with other guidance](combining.md) resolves.

## Omitted findings

The following findings are omitted for each convention:

| Scope | Changelogs | MADR decision records |
| --- | --- | --- |
| Overviews and heading form | `h1-overview`, `topic-overview`, `heading-depth`, `heading-number` | `h1-overview`, `topic-overview` |
| Topic organization | `part-after-topic`, `topic-single-child` | `part-after-topic`, `topic-single-child` |
| Counts and sizes | `list-single`, `list-length`, `section-count`, `sibling-imbalance`, `file-size` | `list-single`, `sibling-imbalance` |
| List introductions | `list-intro`, and `heading-intro` for lists only | None |
| Links into the file, regardless of which file contains the link | `anchor-to-part` | `link-without-summary`, for a link whose text is the record's title |

A changelog omits its findings throughout the file.
A MADR record omits `h1-overview` for the file and the other codes only inside the H2 sections of the MADR templates from 2.1 to 4.0.
These are Context and Problem Statement, Decision Drivers, Considered Options, Decision Outcome, Validation, Pros and Cons of the Options, More Information, and Links.
Sections that a writer adds follow the ordinary rules, and a part that follows a topic is reported unless it is one of these sections.

All other findings remain applicable, including links from these files into ordinary documents.
In a changelog, a table directly under H1 or under a heading with subheadings still needs an introductory paragraph.
In a MADR record, a list or table directly under H1 or a template topic H2 needs one as well.
A paragraph of badges does not count as that introduction.

## Template comments

The MADR 4.0 template puts an HTML comment between the pros and cons of its first option.
A comment at the start of a line ends the list, so the arguments after it get `list-intro`.
Remove the comment when filling in the record, or indent it into the item before it.
