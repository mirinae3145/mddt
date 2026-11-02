# Checker reference

This document describes the checker that comes with the skill.
It covers running the checker, its findings and output, its options, the files it checks, and its exit statuses.
Read it when a run needs options, when choosing files to check or exclude, or when a script reads the output.

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
JSON output lists the checked files, the skipped files, and the findings without fix guidance, and it holds outlines only with `--outline` or `--review`.

## Options

The command accepts these options:

- **`--outline`**: Print how each file was interpreted, even without structural findings.
- **`--review`**: Also report information for reviewing structure, and print every outline.
- **`--format text|json`**: Choose the output format, which defaults to text.
- **`--exclude GLOB`**: Skip files whose path relative to the tree root, or whose name, matches GLOB; repeat it for several patterns.
- **`--root DIR`**: Set the top of the document tree, which decides each document's parent; it defaults to the Git repository root, then to a directory argument.

## Files checked

A file argument is checked as given, and a directory argument expands as follows:

- **In a Git repository**: The `.md` files that Git sees, which are tracked files and untracked files that are not ignored.
  Without the `git` command, every `.md` file is checked, and the checker reports that `.gitignore` was not applied.
- **Outside a repository**: Every `.md` file.
- **Never entered**: The `.git` and `node_modules` folders and folders reached through symbolic links.
  Other hidden folders are checked, so exclude them with `--exclude` when they hold no documents.

Files named CHANGELOG and files matching `--exclude` are skipped even when named explicitly.
Lists inside block quotes are not checked.

## Exit status

The command ends with one of these statuses:

| Status | Meaning |
| --- | --- |
| 0 | No errors were found |
| 1 | At least one error was found |
| 2 | A path does not exist or a file is not readable as UTF-8, and no findings are reported |
