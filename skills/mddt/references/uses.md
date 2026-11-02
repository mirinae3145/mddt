# Applying the document model to common uses

This document applies the [document model](model.md) to three common uses: repository documentation, project records, and agent instructions and skills.
Each use decides which vocabulary of document kinds and which entry documents apply, while the model and the [information types](kinds.md#information-types) stay the same.

## Repository documentation

Repository documentation serves the users and contributors of one repository.
It is organized as follows.

- **Kinds**: Each topic is judged with the Diátaxis compass described in [document kinds](kinds.md#document-kinds), which yields action, reference, and explanation.
- **README**: The root README is the entry document and a landing page.
  It says what the project is, whom it serves, and how to start.
  It links with summaries to CONTRIBUTING, to `docs/README.md`, and to other top-level documents.
- **Kinds within the README**: README sections may differ in kind: installation is action, configuration options are reference, and design is explanation.
  The kind then divides the sections, while each document below `docs/` keeps one kind.
- **The docs folder**: `docs/README.md` is the folder's index, and a document that gains children gets a companion folder.
- **Files outside the checks**: Changelogs follow their own conventions, and Markdown that is not documentation, such as templates and fixtures, is not checked.
  The [checker reference](checker.md#files-checked) says which files a run skips and how to exclude others.

## Project records

Project records keep what a project has learned and decided, so that work can continue across sessions and people.
The project or its workflow decides what to record and whether to keep a given kind of record at all.
This skill only describes how records that a project does keep are structured.

- **Kinds**: Records use their roles as kinds, because a current-state record mixes Diátaxis kinds by nature and a history fits none of them.
  A record's role follows from what its reader does with it, such as checking status, tracing events, or understanding a choice.
- **Roles not listed here**: Plans, validation logs, handoff notes, and other roles take the dominant types that match their reader's task.
- **Files and sections**: Several roles may share one file as sections.
  A role moves to its own file under the same conditions as any topic, as [placing a document](writing.md#placing-a-document) describes.
- **Links between roles**: A link from one record to evidence in another, such as from a current state to its decision, is a lateral link.
  Its sentence says why the link is there.

Projects that keep the following common roles structure them like this:

| Role | Dominant types | Structure |
| --- | --- | --- |
| Current state | Fact, principle | Named lists by category; rewritten as conditions change rather than appended to |
| History | Fact, process | Dated headings or items; dates are a mechanical order, so long lists are fine |
| Decision | Principle, concept | One decision per topic with the choice and its rationale; alternatives compared in a table; reconsideration conditions as principles |

## Agent instructions and skills

Agent instructions and skills are read by agents, often only in part, so their entry documents decide what else gets read.
They are organized as follows.

- **Kinds**: Agent documents use the repository kinds.
  Workflows are action with numbered steps, rule sets and option lists are reference made mostly of principle blocks, and rationale is explanation.
- **Skills**: `SKILL.md` is the entry document and a landing page, and the documents in `references/` are its children.
  The summary next to each link says when to read that document, so an agent loads only what its task needs.
- **Instruction sets**: An entry file introduces supplementary documents, and their own subdocuments go in companion folders, such as `writing.md` with `writing/markdown.md`.
- **Directives**: A default rule comes first and its exceptions after it, as described in [condition placement](model.md#paragraphs-and-sentences).
