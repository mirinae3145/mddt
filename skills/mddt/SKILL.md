---
name: mddt
description: >
  Write, restructure, and read Markdown documents as one tree whose hierarchy
  holds up. Use when creating Markdown documents or adding, moving, or removing
  content in them; when restructuring documents that have grown; when
  navigating a set of Markdown documents to find or verify information; and
  when checking documents against the model. Not needed for edits that stay
  within existing sentences, such as fixing typos, rewording, or updating
  values. Includes a checker for the rules a parser can see.
license: CC-BY-4.0 for the instructions and references; MIT for the scripts; copyright 2026 Taeha Shin
---

# mddt

mddt treats a set of Markdown documents as one tree.
Files link downward to the files they introduce, headings divide each file into topics and parts, and lists nest only where nesting carries meaning.
This file is the entry point, and the rules and procedures live in the reference documents that its parts introduce.

## Document model

The [document model](references/model.md) states the properties a conforming document has.
Writers treat each property as a condition to satisfy, and readers treat it as a guarantee to rely on.
It covers files, headings, sentences, links between documents, sections versus lists and tables, siblings, and lists.
[Examples](references/examples.md) show its judgment rules as before-and-after pairs, and they help when a rule's application is unclear.

When deciding a topic's kind or a block's form, read [document kinds and information types](references/kinds.md).
When writing repository documentation, project records, or agent instructions and skills, read [applying the document model to common uses](references/uses.md).
When a term such as part or division is unclear, look it up in the [terms](references/terms.md), which point to where each term is defined.

## Writing and restructuring

Before creating a document or adding, moving, or removing content in one, read [writing and restructuring](references/writing.md).
It covers planning a document's place in the tree, choosing forms, rules for new writing, growing and shrinking structure, and checking the result.
Read the document model as well, since the writing procedure applies it rather than repeating it.

## Reading

Before exploring a set of Markdown documents to answer a question or verify a fact, read [reading a document tree](references/reading.md).
It explains how to choose files from the tree, why to read them whole, and how to treat documents outside the model.
It also shows which reading strategy each guarantee of the model supports.

## Checking

The checker decides the rules a parser can see and flags the ones that need judgment.
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
