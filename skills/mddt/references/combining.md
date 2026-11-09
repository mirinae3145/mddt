# Combining mddt with other guidance

mddt governs how Markdown documents are structured, so other skills, guidelines, and tools that govern the same documents can complement it or conflict with it.
This document describes guidance that complements mddt, requirements that can conflict with it, and how to resolve such a conflict.

## Complementary guidance

Guidance that covers what mddt leaves out can apply to the same documents alongside it:

- **Technical writing and subject review**: Covers explanation quality, audience, terminology, and whether content is correct about its subject.
- **Markdown formatting and linting**: Covers formatting that the model leaves out, such as list markers, spacing, and code block style.

Such guidance can still prescribe structure, such as a fixed section order, hard-wrapped lines, or heading levels.
Read its actual instructions rather than judging it by its name, and treat each structural requirement in it as a possible conflict.

## Conflicting requirements

Requirements conflict when they ask the same documents for structure that the [document model](model.md) or the [reading procedure](reading.md) rules out, as in these cases:

| Source | Requirement | Rule it can break |
| --- | --- | --- |
| Formatter or linter | Hard wrapping at a fixed line width | One sentence per line |
| Another document organization skill | Its own heading depth, file boundaries, parent links, or list nesting | Files hold topics, downward links, and nesting |
| Required template or deliverable | Fixed headings and order, or a single file | Headings and promotion, and files hold topics |
| Excerpt-based retrieval | Answers drawn from search excerpts | Reading files whole |

Search itself does not conflict with mddt, since the reading procedure keeps it for documents outside the model.

## Resolving a conflict

Resolve a conflict for the documents it concerns with these steps:

1. Check whether the model already accommodates the requirement, as with the changelog exceptions in [repository documentation](uses.md#repository-documentation).
1. Let the instructions that govern the task decide which requirement prevails, such as the user's request or the repository's contributor guidance.
   When they leave the choice open, ask the user which convention to follow.
1. Apply the prevailing requirement, and apply the model wherever that requirement leaves structure open.
1. Report which model properties the documents give up, and keep the checker findings that follow from them.

Settle each conflict once, so that the two sets of guidance do not take turns undoing each other's fixes.
A document that keeps a required format stays checked, so its links and the parts that the format leaves open are still judged.
The [ignore file](ignore-file.md) is only for documents that the collection does not write to the model at all.
