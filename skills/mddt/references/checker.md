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

Without uv, install `markdown-it-py` and `mdit-py-plugins` and run the script with Python.

## Findings

Each finding has a code and one of three severities:

- **Error**: A violation that the parser can decide.
- **Warning**: A place that needs a writer's judgment, where keeping the original structure is a valid outcome.
- **Information**: Support for a deliberate review of structure, shown only with `--review`.

The codes, their severities, and their rule locations are listed in `scripts/rules.toml`.
Information findings rest on approximate detection, so judge each one before acting on it.
For example, a summary in a table cell beside a link is not recognized.
An item counts as a block by its number of sentences alone.

## Output

Text output prints each code once with its summary and rule location, then every location where it occurs, then its fix guidance.
Files with structural findings also get an outline that shows how the checker interpreted them.

JSON output is an object whose keys `files` and `skipped` list the checked and skipped files.
Its key `diagnostics` lists the findings without fix guidance, each with the fields `file`, `line`, `endLine`, `code`, `severity`, and `message`.
The message joins the code's summary and the finding's detail, and the key `outlines` appears only with `--outline` or `--review`.

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
  Without the `git` command, files are found as outside a repository, and the checker reports that `.gitignore` was not applied.
- **Outside a repository**: Every `.md` file, except in folders whose own `.gitignore` holds only `*`.
  Tools such as pytest and uv mark their caches and virtual environments this way.
- **Never entered**: The `.git` and `node_modules` folders and folders reached through symbolic links.
  Other hidden folders are checked, so exclude them with `--exclude` when they hold no documents.

Files named CHANGELOG and files matching `--exclude` are skipped even when named explicitly.
Lists inside block quotes are not checked.
YAML front matter and HTML blocks, such as comments, are not judged as prose, and they neither introduce nor separate the blocks around them.

## Links checked

Links in the checked files are resolved as follows, while images and links written in raw HTML are not checked:

- **Paths**: A relative path is resolved from the linking file's folder after percent-decoding, and a missing file or folder is an error.
  A link to a folder stands for the folder's index file when it has one.
- **Anchors**: An anchor in a link to a Markdown file, or a bare `#anchor`, must match a heading ID or an HTML `id` or `name` in its target.
  A heading ID is the heading text in lowercase, without punctuation, with spaces as hyphens, and with `-1`, `-2`, and so on for repeats.
- **Anchor IDs**: This rule only approximates GitHub's, so a missing anchor is a warning.
  For example, GitHub keeps the variation selector that follows some emoji, while the checker drops it, so anchors to such headings are reported falsely.
- **Not resolved**: URLs with a scheme and absolute paths are left alone, since their base depends on where the documents are served.
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
| 2 | A path does not exist or a file is not readable as UTF-8, and no findings are reported |
