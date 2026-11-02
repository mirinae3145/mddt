---
name: mddt
description: >
  Write, restructure, and read Markdown documents as a tree of files, topics,
  sections, and lists whose hierarchy holds up. Use when creating or
  substantially editing Markdown documentation, project records, agent
  instructions, or skills; when restructuring documents that have grown; and
  when navigating a set of Markdown documents to find or verify information.
  Includes a checker for the structural rules.
license: CC-BY-4.0 for the instructions and references; MIT for the scripts
---

# mddt

mddt treats a set of Markdown documents as one tree.
Files link downward to the files they introduce, headings divide each file into topics and parts, and lists nest only where nesting carries meaning.
This file is the entry point; the rules and procedures live in the reference documents linked below.

## Document model

The [document model](references/model.md) states the properties a conforming document has.
Writers treat each property as a condition to satisfy, and readers treat it as a guarantee to rely on.
It covers files, headings, sentences, links between documents, sections versus lists and tables, siblings, and lists.
[Examples](references/examples.md) show its judgment rules as before-and-after pairs; read them when a rule's application is unclear.

[Document kinds and information types](references/kinds.md) decide what a topic contains and which form each block takes by default.
Read [applying the document model to common uses](references/uses.md) when writing repository documentation, project records, or agent instructions and skills.

## Writing and restructuring

Read [writing and restructuring](references/writing.md) before creating a document or substantially editing one.
It covers planning a document's place in the tree, choosing forms, growing and shrinking structure, and checking the result.
Read the document model as well, since the writing procedure applies it rather than repeating it.

## Reading

Read [reading a document tree](references/reading.md) before exploring a set of Markdown documents to answer a question or verify a fact.
It explains how to choose files from the tree, why to read chosen files whole, and how to treat documents outside the model.

## Checking

The checker decides the structural rules a parser can see and flags the ones that need judgment.
Run it on the Markdown files you created or changed:

```bash
uv run <skill-dir>/scripts/mddt.py FILE...
```

Each finding comes with fix guidance, and errors make the command exit with status 1.
Apply the findings as described in [checking](references/writing.md#checking), which limits them to what the current task created or made worse, unless the user asked for restructuring.
When a run needs options or other files, or a script reads its output, read the [checker reference](references/checker.md).
It covers running the checker, its findings and output, its options, the files it checks, and its exit statuses.

## Scope

This skill covers hierarchy, not formatting or prose quality.
Run the repository's own Markdown linter for formatting rules.
For the quality of explanations and tutorials, use this skill together with a technical writing skill or guideline, if one is available.
Academic papers follow their own conventions and are out of scope.
