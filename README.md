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
When a file has structural findings, the output also shows how the checker interpreted the file.
`--outline` shows this interpretation for every file, and `--format json` produces machine-readable output.

Changelogs follow their own conventions and are skipped.
Codes and their severities are listed in [`rules.toml`](skills/mddt/scripts/rules.toml).

The checker covers structure only.
Run your own Markdown linter separately for formatting rules.
