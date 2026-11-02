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

The document model draws on these works and style guides:

- **[DITA](https://docs.oasis-open.org/dita/dita/v1.3/dita-v1.3-part0-overview.html) and [Lightweight DITA](https://docs.oasis-open.org/dita/LwDITA/v1.0/cn01/LwDITA-v1.0-cn01.html)**: topic orientation, maps, and information typing.
- **[Diátaxis](https://diataxis.fr/)** by Daniele Procida: document kinds and the compass that tells them apart.
- **[Information Mapping](https://informationmapping.com/)** by Robert E. Horn: information types, labeled blocks, and decision tables.
- **[The Pyramid Principle](https://www.barbaraminto.com/)** by Barbara Minto: questions and answers between levels, and divisions without gaps or overlaps.
- **[Every Page is Page One](https://everypageispageone.com/the-book/)** by Mark Baker: self-contained topics, siblings at one level of detail, and links within sentences.
- **[Google](https://developers.google.com/style) and [Microsoft](https://learn.microsoft.com/en-us/style-guide/welcome/) style guides**: conventions for lists and tables.

The model interprets these sources selectively and arranges and reconstructs their ideas into one set of rules.
It does not represent any source in full or the positions of its authors.

## Checker

The checker reads the Markdown files or directories it is given and reports findings by code.
It needs Python 3.11 or later and [uv](https://docs.astral.sh/uv/), which installs the dependencies declared in the script.

```bash
uv run skills/mddt/scripts/mddt.py README.md docs/
```

Without uv, install `markdown-it-py` and `mdit-py-plugins` and run the script with Python.

Errors are violations the parser can decide, and the command exits with status 1 when any are found.
Warnings mark places that need a writer's judgment, and keeping the original structure is a valid outcome for them.
Information supports a deliberate review of structure and appears only with `--review`.
Each code is printed once with its summary and rule location, followed by every location where it occurs and then its fix guidance.
Codes and their severities are listed in [`rules.toml`](skills/mddt/scripts/rules.toml).

`--outline` prints how each file was interpreted, and files with structural findings get it automatically.
`--review` adds review information and prints the outline of every file.
Run the checker with `--help` for its other options, the files a directory run checks, and its exit statuses.
Its numeric thresholds were reviewed against documents written to the model, as [calibration](calibration/README.md) describes.
The checker covers structure only, so run your repository's own Markdown linter for formatting rules.

## Limits

What makes a document good to read and write can differ between people and agents.
The model builds on sources that were written with human readers in mind.
In the maintainer's judgment, the skill is effective at getting agents to write better documents.
Its effect on agents as readers of those documents has not been tested.

Following the skill can cost more than writing without it.
An agent reads the reference documents, plans each document's place in the tree, and revises the document after running the checker.
These steps take more tokens and time than a direct edit.

The checker counts words as whitespace-separated tokens that contain a letter or digit, so one rule covers English words and Korean eojeol.
Sentence boundaries were reviewed with English and Korean documents, and the sentence length threshold with English documents written to the model.
Korean sentences written to the same model contain fewer words, so the threshold rarely applies to them.
Sentence boundaries inside a line are recognized after Korean sentence endings and full-width stops and before capital letters, so other languages may get incomplete `line-sentences` findings.
Languages written without spaces between words, such as Chinese, Japanese, and Thai, are not measured meaningfully.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how the checker is organized and how to run its tests.

## License

The checker and its tests are licensed under the MIT License.
The documentation, including the skill's instructions and reference documents, is licensed under CC BY 4.0.
[`REUSE.toml`](REUSE.toml) assigns each path its license, following the [REUSE](https://reuse.software/) specification, and the license texts are in [`LICENSES/`](LICENSES/).

## AI disclosure

Claude by Anthropic assisted with the design, implementation, documentation, and tests of this project.
The maintainer directed the design and decided its rules.
The skill is written for AI agents, and the checker's findings support a writer's judgment rather than replace it.
