# MDDT &mdash; Markdown Document Tree

`mddt` is an agent skill for writing and reading Markdown documents whose hierarchy holds up.
It covers how documents link into a tree, how far sections nest, and how lists carry structure in their nesting.
The skill guides an agent through writing, restructuring, and reading such documents, and a checker verifies the structural rules.

## Install

The skill is the folder `skills/mddt/`, and it works with agents that read `SKILL.md` skills.
Link or copy the whole folder into your agent's skill directory, keeping `SKILL.md`, `references/`, and `scripts/` together.

## Document model

The skill's [document model](skills/mddt/references/model.md) describes how a conforming Markdown file is organized.
Its central rules are these.

- **Files and topics**: A file is either one topic or a set of topics, never a set of sets.
  Its H1 and the overview paragraph below it identify the file.
- **Topics and parts**: An H2 with H3 children is a topic and needs its own overview paragraph.
  An H2 without H3 children is a part of its parent.
  Headings stop at H3; content that needs H4 moves to its own file.
- **Lists**: A list starts with an introductory sentence unless it is the only content of its section.
  Lists nest at most three levels, and a named item does not contain named items.

## Checker

The checker reads the Markdown files or directories it is given and reports findings by code.
It needs Python 3.11 or later and [uv](https://docs.astral.sh/uv/), which installs the dependencies declared in the script.

```bash
uv run skills/mddt/scripts/mddt.py README.md docs/
```

Without uv, install `markdown-it-py` and `mdit-py-plugins` and run the script with Python.

Errors are violations the parser can decide, and the command exits with status 1 when any are found.
Warnings mark places that need a writer's judgment, and keeping the original structure is a valid outcome for them.
Each code is printed once with its fix guidance, followed by every location where it occurs.
Codes and their severities are listed in [`rules.toml`](skills/mddt/scripts/rules.toml).

The command accepts these options:

- `--outline` prints how each file was interpreted; files with structural findings get it automatically.
- `--format json` produces machine-readable output.
- `--exclude GLOB` skips files that are not documents, such as templates and test fixtures.
- `--root DIR` sets the top of the document tree, which decides each document's parent.
  It defaults to the Git repository root, then to a directory argument.

Changelogs are always skipped.
The checker covers structure only, so run your repository's own Markdown linter for formatting rules.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how the checker is organized and how to run its tests.
