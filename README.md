# MDDT &mdash; Markdown Document Tree

`mddt` is an agent skill for writing and reading Markdown documents whose hierarchy holds up.
It covers how documents link into a tree, how far sections nest, and how lists carry structure in their nesting.
The skill gives an agent procedures for writing, restructuring, and reading such documents.
A checker decides the rules a parser can see, while the writer judges the rest by following those procedures.
The repository follows the model it presents, as [self-conformance](CONTRIBUTING.md#self-conformance) describes.

To make mddt part of a repository's writing conventions, start from [adopting mddt in a repository](skills/mddt/references/adopting.md), which the skill includes.

## Install and use

The skill is the folder `skills/mddt/`, and it works with agents that read `SKILL.md` skills.
Link or copy the whole folder into your agent's skill directory, keeping `SKILL.md`, `references/`, and `scripts/` together.

Once installed, the agent follows the skill's procedures, which say how to write and read documents that meet the [document model](skills/mddt/references/model.md).
Some requirements live only in the procedures, such as placing content before writing it, rewriting summaries once content settles, and rereading changed topics whole.

- **[Writing and restructuring](skills/mddt/references/writing.md)**: Places content, chooses forms, restructures trees as content changes, and checks the result by rereading and running the checker.
- **[Reading](skills/mddt/references/reading.md)**: Chooses files from the tree, reads them whole, and relies on the model's guarantees.

A repository that adopts mddt for its documents therefore points its contributors to the skill and its procedures, not to the model alone.

The skill covers structure, so other skills and tools often govern the same documents.
[Combining mddt with other guidance](skills/mddt/references/combining.md) says which of them complement it and how to resolve their conflicts with it.

## Document model

The skill's [document model](skills/mddt/references/model.md) describes the properties that a conforming Markdown document has.
It covers files, headings, sentences, links between documents, sections versus lists and tables, siblings, and lists.

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
It decides the rules a parser can see and flags some others for judgment.
Rules that depend on meaning, such as where content belongs and whether a summary is accurate, stay with the writer.
A run without findings therefore does not show that a document conforms to the model.

Changelogs are checked with exceptions that preserve their release structure, as [common uses](skills/mddt/references/uses.md#repository-documentation) describes.
Its length checks use a local English parsing model to count independent clauses joined by semicolons, colons, or dashes separately.
Its numeric thresholds were reviewed against documents written to the model, as [calibration](calibration/README.md) describes, before the length checks counted such clauses separately.

The [checker reference](skills/mddt/references/checker.md) covers running the checker, its findings and output, its options, the files and links it checks, and its exit statuses.
The checker does not cover formatting, which a repository's own Markdown linter can check.

## Limits

What makes a document good to read and write can differ between people and agents.
The model builds on sources that were written with human readers in mind.
In the maintainer's judgment, the skill is effective at getting agents to write better documents.
Its effect on agents as readers of those documents has not been tested.

Following the skill can cost more than writing without it.
An agent reads the reference documents, plans each document's place in the tree, rereads what it changed, and revises the document after running the checker.
These steps take more tokens and time than a direct edit.
They are also where the judgment rules are applied, so skipping them leaves only what the checker can see.

The checker counts words as whitespace-separated tokens that contain a letter or digit.
Its [sentence units](skills/mddt/references/model.md#paragraphs-and-sentences) differ from grammatical sentences, and their boundaries depend partly on the English parsing model.
Its length thresholds were calibrated on whole sentences in English documents written to the model, so their fit to sentence units remains open.
Sentence boundaries inside a line are recognized after Korean sentence endings and full-width stops and before capital letters, so other languages may get incomplete `line-sentences` findings.
Languages written without spaces between words, such as Chinese, Japanese, and Thai, are not measured meaningfully.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for what to read before a change, how the checker is organized, and what to update when a rule changes.
It also says how the repository applies the skill to itself, how files are licensed, and how to verify changes.

## License

The checker and its tests are licensed under the MIT License.
The documentation, including the skill's instructions and reference documents, is licensed under CC BY 4.0.
[`REUSE.toml`](REUSE.toml) assigns each path its license, following the [REUSE](https://reuse.software/) specification, and the license texts are in [`LICENSES/`](LICENSES/).

## AI disclosure

Claude by Anthropic and Codex by OpenAI assisted with the design, implementation, documentation, and tests of this project.
The maintainer directed the design and decided its rules.
The skill is written for AI agents, and the checker's findings support a writer's judgment rather than replace it.
