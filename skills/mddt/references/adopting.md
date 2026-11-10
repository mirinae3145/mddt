# Adopting mddt in a repository

This guide is for maintainers and agents who make mddt part of a repository's writing conventions.
It covers choosing documents and their entries, what the contributor guidance states, the first restructuring, and an optional CI check.
Take the steps in this order, because each one relies on the one before it.

## Documents in scope

Decide which Markdown files follow the model before changing any of them.
Documentation that people or agents read follows it, including README, contributor guidance, guides, and agent instructions and skills.
Identify the entry of each independent tree in scope, and introduce from the repository README those that its readers need, with summaries.

Leave out documents that are not meant to follow it, such as user-provided originals, generated material, templates, and fixtures.
List them in a `.mddtignore`, as the [ignore file](ignore-file.md) describes, so that every check skips them.

Changelogs need no entry, because the checker already applies their [conventions](uses.md#repository-documentation).
The repository's Markdown linter keeps its formatting rules, which mddt does not cover.

## Contributor guidance

The repository's contributor guidance makes the skill's procedures a requirement for Markdown changes.
A link to the document model alone is not enough.
Some requirements live only in the procedures, such as placing content first and rereading changed topics whole.
The guidance states the following:

- **Procedures**: Contributors follow the [writing procedure](writing.md) before and after editing Markdown.
  The guidance names both ends of it: placing content before writing, and rereading changed topics whole once the content settles.
  Sentence-only corrections and formatting changes that leave the structure as it was need no placement plan.
- **Getting the skill**: Contributors use an installed copy of the skill or a checkout of the mddt repository.
  Either one gives them the reference documents and the checker.
- **Repository placement**: The guidance adds only what is specific to the repository.
  Examples are what the README holds, where canonical contracts live, and which index introduces the guides.
  Link to the procedures for their full steps rather than restating them, so that the guidance does not fall behind mddt.
  A summary that keeps only the checker's part, such as running it and judging its findings, invites skipping the rest.
- **Role of the checker**: Writers and reviewers judge placement, kinds, and summaries, which the checker does not decide.
  A run without errors is the minimum, not evidence that a document conforms.
- **Reports**: A change that keeps a warning after judgment can say why where reviewers will see it, such as in the change description.
  Require more, such as the checker revision or the files checked, only when the repository already records validation that way.

The guidance can open with sentences like the following, which name the procedure before the model or the checker:

```markdown
For Markdown changes, follow the mddt skill's writing procedure.
Place content in the document tree before writing it, and reread each changed topic whole once it settles.
The checker then covers only the requirements a parser can decide.
```

Point to this guidance from the contributing guide, where contributors look before a change.
Add it before the first restructuring, or in the same change, so that reviewers judge the restructuring against it.

## First restructuring

Existing documents rarely follow the model, so adoption usually starts with a restructuring of the whole collection.
Carry it out as [restructuring an existing tree](writing.md#restructuring-an-existing-tree) describes, as a change of its own rather than alongside other work.
Its baseline of findings shows where the documents started, and it is not a target to drive to zero.
Warnings that remain after judgment are a valid outcome, as [checking](writing.md#checking) describes.

## Continuous integration

A CI job can run the checker as an automated minimum check, but it is optional and does not replace review.
A job that fits the checker's design has these properties:

- **Errors on the whole repository**: Errors fail the job in every file.
  A moved or renamed file can break links in files that a change did not edit.
  A missing anchor is only a warning, because the checker approximates heading IDs, so this check does not catch renamed headings.
- **Warnings on changed files**: Warnings call for a writer's judgment, so the job reports them only in changed files and does not fail on them.

The job either pins a revision of the mddt repository or follows its current default branch.
Both are valid, and each asks for its own upkeep:

| Approach | Findings | Upkeep |
| --- | --- | --- |
| Pinned revision | Change only when the pin changes, so a run can be reproduced | Update the pin in a change of its own, since new rules can report errors in untouched documents; contributors whose local skill differs tell the two sets of findings apart |
| Current branch | Follow the latest rules and fixes without a change to the repository | Print the commit each run used, since a new rule can fail the job without a change to the repository |

The [checker reference](checker.md) describes the output formats and exit statuses that a CI script reads.
