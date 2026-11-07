---
name: mddt
description: >
  Write, restructure, and read Markdown documents with coherent structure
  within and across files. Use when creating documents or adding, moving, or
  removing content; choosing document boundaries or organizing headings,
  lists, and tables; reviewing structure against the model; navigating a
  set of Markdown documents to find or verify information; or making mddt
  part of a repository's writing conventions. Not needed for
  edits confined to existing sentences, such as typo fixes, rewording, or
  value updates, or for formatting-only changes that leave structure unchanged.
license: CC-BY-4.0 for the instructions and references; MIT for the scripts; copyright 2026 Taeha Shin
---

# mddt

mddt organizes Markdown documents into trees, each with an entry document.
A collection can hold several independently entered trees.
Files link downward to the files they introduce, headings divide each file into topics and parts, and lists nest only where nesting carries meaning.
This file is the entry point, and the rules and procedures live in the reference documents that its parts introduce.

## Document model

The [document model](references/model.md) states the properties of conforming documents and their trees.
Writers treat each property as a condition to satisfy, and readers treat it as a guarantee to rely on.
It covers files, headings, sentences, links between documents, sections versus lists and tables, siblings, and lists.
[Examples](references/examples.md) show its judgment rules as before-and-after pairs, and they help when a rule's application is unclear.

When deciding a topic's kind or a block's form, read [document kinds and information types](references/kinds.md).
When writing repository documentation, project records, or agent instructions and skills, read [applying the document model to common uses](references/uses.md).
When a term such as part or division is unclear, look it up in the [terms](references/terms.md), which point to where each term is defined.

## Writing and restructuring

Before creating a document or adding, moving, or removing content in one, read [writing and restructuring](references/writing.md).
It covers planning a document's place in the tree, choosing forms, and rules for new writing.
It also covers growing and shrinking structure, restructuring an existing tree, and checking the result.
Read the document model as well, since the writing procedure applies it rather than repeating it.

When making mddt part of a repository's writing conventions, read [adopting mddt in a repository](references/adopting.md).
It covers the documents in scope, what contributor guidance requires, the first restructuring, and an optional CI check.

## Reading

Before exploring a set of Markdown documents to answer a question or verify a fact, read [reading a document tree](references/reading.md).
It explains how to select an entry, choose files, read them whole, and handle documents outside the model.
It also shows which reading strategy each guarantee of the model supports.

## Checking

The checker decides the rules a parser can see and flags some that need judgment.
It does not replace the reread that [checking](references/writing.md#checking) starts with, where the writer applies the other judgment rules.
Run it on the Markdown files you created or changed:

```bash
uv run <skill-dir>/scripts/mddt.py FILE...
```

Each finding comes with fix guidance, and errors make the command exit with status 1.
Apply the findings as described in [checking](references/writing.md#checking), which limits them to what the current task created or made worse.
A requested restructuring applies more of them, though not every sentence-level finding.
The [checker reference](references/checker.md) covers running the checker, its findings and output, its options, the files and links it checks, and its exit statuses.
Read it in these cases:

- **File selection**: A run takes a directory, excludes files, or sets the tree root.
- **Scripts**: A script or CI job reads the output or the exit status.
- **Setup**: uv is not available.

A tree can hold documents that do not follow the model, such as a user's originals or generated material.
A `.mddtignore` file leaves them out of the check, as the [ignore file](references/ignore-file.md) describes.

## Scope

This skill covers the structure of Markdown documents, together with the paragraph and sentence rules that support it.
It leaves formatting, prose quality, and whether content is correct about its subject to other guidance.
Summaries in parent documents still have to stay accurate to the documents they condense.
Academic papers follow their own conventions and are out of scope.

When another skill, guideline, or tool also governs the documents a task writes or reads, read [combining mddt with other guidance](references/combining.md).
It covers which guidance complements mddt, which requirements can conflict with it, and how to resolve a conflict.
