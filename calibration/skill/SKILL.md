---
name: mddt
description: >
  Write, restructure, and read Markdown documents as a tree of files, topics,
  sections, and lists whose hierarchy holds up. Use when creating or
  substantially editing Markdown documentation, project records, agent
  instructions, or skills; when restructuring documents that have grown; and
  when navigating a set of Markdown documents to find or verify information.
---

# mddt

mddt treats a set of Markdown documents as one tree.
Files link downward to the files they introduce, headings divide each file into topics and parts, and lists nest only where nesting carries meaning.
This file is the entry point; the rules and procedures live in the reference documents linked below.

## Document model

The [document model](references/model.md) states the properties a conforming document has.
Writers treat each property as a condition to satisfy, and readers treat it as a guarantee to rely on.
It covers files and topics, headings and promotion, paragraphs and sentences, links between documents, the choice between sections, lists, and tables, and list structure.
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

After writing, review the result against the [document model](references/model.md) and fix what does not conform.

## Scope

This skill covers hierarchy, not formatting or prose quality.
Run the repository's own Markdown linter for formatting rules.
For the quality of explanations and tutorials, use this skill together with a technical writing skill or guideline, if one is available.
Academic papers follow their own conventions and are out of scope.
