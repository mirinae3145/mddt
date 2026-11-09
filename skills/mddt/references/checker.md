# Checker reference

This document describes the checker that comes with the skill.
It covers running the checker, its findings and output, its options, the files and links it checks, and its exit statuses.
Read it when choosing the files or tree root of a run, when a script reads the output or exit status, or without uv.

## Running

The checker is `scripts/mddt.py` in the skill folder.
It needs Python 3.11 or later, and [uv](https://docs.astral.sh/uv/) installs the dependencies declared in the script:

```bash
uv run <skill-dir>/scripts/mddt.py FILE...
```

The dependencies include spaCy 3.8.18 and its English model `en_core_web_md` 3.8.0, pinned together to keep sentence analysis reproducible.
uv downloads the model wheel from the official spaCy model releases with the other dependencies.
Without uv, install every dependency in the script's metadata into the Python environment used to run it.
The checker loads the model locally when prose contains a possible clause boundary; it sends no document text to a service.

## Findings

Each finding has a code and one of three severities:

- **Error**: A violation that the parser can decide.
- **Warning**: A place that needs a writer's judgment, where keeping the original structure is a valid outcome.
- **Information**: Support for a deliberate review of structure, shown only with `--review`.

The codes, their severities, and their rule locations are listed in `scripts/rules.toml`.
Information findings rest on approximate detection, so judge each one before acting on it.
For example, a summary in a table cell beside a link is not recognized.
An item counts as a block by its number of sentences alone.

Length checks apply the [sentence unit rule](model.md#paragraphs-and-sentences) as follows:

- **Boundaries**: Semicolons, colons, and em or en dashes between complete English clauses divide units, including imperative instructions without subjects.
  The checker uses dependency parsing to distinguish complete clauses from enumeration, subordinate clauses, and inserted phrases.
- **Kept together**: Conjunctions and commas do not add boundaries, and wrapping a line after a colon does not end a unit.
  List item labels and bracketed material stay with their enclosing prose.
  The line layout and list item naming checks keep their existing sentence boundaries.
- **Limits**: This analysis is an estimate from an English model, not a grammar guarantee.
  The numeric thresholds predate these additional boundaries, so their suitability for sentence units remains a matter for review.
- **Other languages**: Non-Latin text receives no additional clause boundaries, and other Latin-script languages are outside the model's scope.
  The thresholds were calibrated with English documents only, so length findings in other languages need more judgment.

The `line-sentences` check finds a new sentence inside a line only after a Korean sentence ending or a full-width stop, or before a capital letter.
Other languages can therefore miss its findings.

For `part-after-topic`, the checker recognizes [README closing sections](uses.md#repository-documentation) by a limited set of titles.
In files named `README.md`, it exempts the final consecutive group of H2s with these titles:

- **License notices**: License, Licenses, Licence, Licences, Copyright.
- **Credits and citation**: Acknowledgments, Acknowledgements, Credits, Citation, Citing, AI disclosure.
- **Contribution pointers**: Contributing.

File names and titles are compared without case, and title whitespace and inline formatting do not affect matching.
The closing group is left out when checking date or number order among the preceding H2s.
Other titles, including translations and combined titles, need judgment; a warning can remain when they serve the same closing role.
The exception changes only ordering findings, so the sections retain their topic or part roles and their other checks.

## Output

Text output prints each code once with its summary and rule location, then every location where it occurs, then its fix guidance.
Files with structural findings also get an outline that shows how the checker interpreted them.

JSON output is an object whose keys `files` and `skipped` list the checked and skipped files.
Its key `diagnostics` lists the findings without fix guidance, each with the fields `file`, `line`, `endLine`, `code`, `severity`, and `message`.
The message joins the code's summary and the finding's detail, and the key `outlines` appears only with `--outline` or `--review`.

Both formats are written in UTF-8 regardless of the locale, so headings and file names in any language keep their characters.

## Options

The command accepts these options:

- **`--outline`**: Print how each file was interpreted, even without structural findings.
- **`--review`**: Also report information for reviewing structure, and print every outline.
- **`--format text|json`**: Choose the output format, which defaults to text.
- **`--exclude GLOB`**: Skip files whose path relative to the tree root, or whose name, matches GLOB; repeat it for several patterns.
  Without a tree root, the path is taken relative to the current directory.
- **`--root DIR`**: Set the top of the document tree, which decides each document's parent; it defaults to the Git repository root, then to a directory argument.

## Files checked

A file argument is checked as given, and a directory argument expands as follows:

- **In a Git repository**: The `.md` files that Git sees, which are tracked files and untracked files that are not ignored.
  Subfolders without listed Markdown files are not entered.
  Without the `git` command, files are found as outside a repository, and the checker reports that `.gitignore` was not applied.
- **Outside a repository**: Every `.md` file, except in folders whose own `.gitignore` holds only `*`.
  Tools such as pytest and uv mark their caches and virtual environments this way.
- **Never entered**: The `.git` and `node_modules` folders and folders reached through symbolic links.
  Other hidden folders are checked, so exclude them with `--exclude` when they hold no documents.

Files matching `--exclude` and files a `.mddtignore` ignores are skipped even when named explicitly.
A skipped file is listed as skipped and is not judged, but it stays in the tree.
Links to it still resolve, and it still serves as a parent that must link its children.
The [ignore file](ignore-file.md) describes `.mddtignore`, which lists the files of a folder to skip.
An unreadable input file or traversed folder ends the run with status 2 and no findings.

Changelogs are checked with the exceptions in [repository documentation](uses.md#repository-documentation).
The checker recognizes names matching `CHANGELOG` or `CHANGELOG.*`, without regard to case, including `CHANGELOG.md` and `changelog.en.md`.
Directory searches still select only `.md` files; other matching names can be given explicitly.
Other filenames use the ordinary document rules.

The following findings are omitted for changelogs:

| Scope | Codes omitted |
| --- | --- |
| Overviews and heading form | `h1-overview`, `topic-overview`, `heading-depth`, `heading-number` |
| Topic organization | `part-after-topic`, `topic-single-child` |
| Counts and sizes | `list-single`, `list-length`, `section-count`, `sibling-imbalance`, `file-size` |
| List introductions | `list-intro`, and `heading-intro` for lists only |
| Links into changelogs | `anchor-to-part`, regardless of which file contains the link |

All other findings remain applicable, including table introductions and links from a changelog into ordinary documents.
Outlines show heading levels and list statistics without topic, part, or overview labels.

Lists inside block quotes are not checked.
YAML front matter and HTML blocks, such as comments, are not judged as prose, and they neither introduce nor separate the blocks around them.
Only comments parsed as HTML are excluded from prose; delimiters written as code leave the surrounding prose checked.

## Links checked

Links in the checked files are resolved as follows, while images and links written in raw HTML are not checked:

- **Paths**: A relative path is resolved from the linking file's folder after percent-decoding, and a missing file or folder is an error.
  A link to a folder stands for the folder's index file when it has one.
- **Anchors**: An anchor in a link to a Markdown file, or a bare `#anchor`, must match a heading ID or an HTML `id` or `name` in its target.
  A heading ID is the heading text in lowercase, without punctuation, with spaces as hyphens, and with `-1`, `-2`, and so on for repeats.
  Generated IDs also reserve their names, so a suffix is increased until it conflicts with no earlier ID.
  An HTML element can provide both `id` and `name` anchors; comments and attributes without values provide none.
- **Anchor IDs**: This rule only approximates GitHub's, so a missing anchor is a warning.
  For example, GitHub keeps the variation selector that follows some emoji, while the checker drops it, so anchors to such headings are reported falsely.
- **Own repository on GitHub**: A link into a branch of the linking file's own repository is resolved in the working tree.
  An example is `https://github.com/owner/name/blob/main/CONTRIBUTING.md`.
  The repository is the one whose `origin` remote is on GitHub, and links to commits or tags are left alone.
  This lets a README use full URLs, as packages often need, and still place its children in the tree.
- **Not resolved**: Other URLs with a scheme and absolute paths are left alone, since their base depends on where the documents are served.
  Anchors are also left alone when the link has a query, such as `?plain=1`, or its target is not a Markdown file.
- **Linked trees**: A target reached through a symbolic link, such as a linked repository, is checked only for existence.
  Its headings belong to another tree, which the checker does not enter.

Formulas in dollar math are read as math, so brackets and parentheses in them do not form links.

## Exit status

The command ends with one of these statuses:

| Status | Meaning |
| --- | --- |
| 0 | No errors were found |
| 1 | At least one error was found |
| 2 | An input cannot be read or the English sentence model cannot be loaded, and no findings are reported |
