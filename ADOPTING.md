# Adopting mddt in a repository

This guide is for maintainers who make mddt part of a repository's writing conventions.
It covers choosing the documents that follow the model, what the contributor guidance states, the first restructuring, and an optional CI check.
Take the steps in this order, because each one relies on the one before it.

## Documents in scope

Decide which Markdown files follow the model before changing any of them.
Documentation that people or agents read follows it, including README, contributor guidance, guides, and agent instructions and skills.

Leave out documents that are not meant to follow it, such as user-provided originals, generated material, templates, and fixtures.
List them in a `.mddtignore`, as the [ignore file](skills/mddt/references/ignore-file.md) describes, so that every check skips them.

Changelogs need no entry, because the checker already applies their [conventions](skills/mddt/references/uses.md#repository-documentation).
The repository's Markdown linter keeps its formatting rules, which mddt does not cover.

## Contributor guidance

The repository's contributor guidance makes the skill's procedures a requirement for Markdown changes.
A link to the document model alone is not enough.
Some requirements live only in the procedures, such as placing content first and rereading changed topics whole.
The guidance states the following:

- **Procedures**: Contributors follow the [writing procedure](skills/mddt/references/writing.md) before and after editing Markdown.
  Sentence-only corrections and formatting changes that leave the structure as it was need no placement plan.
- **Getting the skill**: Contributors use an installed copy of the skill or a checkout of this repository.
  Either one gives them the reference documents and the checker.
- **Repository placement**: The guidance adds only what is specific to the repository.
  Examples are what the README holds, where canonical contracts live, and which index introduces the guides.
  Link to the procedures instead of restating their steps, so that the guidance does not fall behind mddt.
- **Role of the checker**: Writers and reviewers judge placement, kinds, and summaries, which the checker does not decide.
  A run without errors is the minimum, not evidence that a document conforms.
- **Reports**: A change reports the checker revision, the files it checked, and the findings kept after judgment with their reasons.

Point to this guidance from the contributing guide, where contributors look before a change.
Add it before the first restructuring, or in the same change, so that reviewers judge the restructuring against it.

## First restructuring

Existing documents rarely follow the model, so adoption usually starts with a restructuring of the whole tree.
Carry it out as [restructuring an existing tree](skills/mddt/references/writing.md#restructuring-an-existing-tree) describes, as a change of its own rather than alongside other work.
Its baseline of findings shows where the documents started, and it is not a target to drive to zero.
Warnings that remain after judgment are a valid outcome, as [checking](skills/mddt/references/writing.md#checking) describes.

## Continuous integration

A CI job can run the checker as an automated minimum check, but it is optional and does not replace review.
A job that fits the checker's design has these properties:

- **Pinned revision**: The job runs the checker from a fixed revision of this repository, so that results do not change with new rules.
  Update the pin in a change of its own, because new rules can report errors in documents that the change did not touch.
- **Errors on the whole tree**: Errors fail the job in every file.
  A moved or renamed heading can break links in files that a change did not edit.
- **Warnings on changed files**: Warnings call for a writer's judgment, so the job reports them only in changed files and does not fail on them.
- **Local and pinned results**: A contributor whose local skill differs from the pinned revision tells the two sets of findings apart.

The [checker reference](skills/mddt/references/checker.md) describes the output formats and exit statuses that a CI script reads.
