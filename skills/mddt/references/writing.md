# Writing and restructuring

This procedure applies the [document model](model.md) when creating a document or changing its structure.
It covers placing a document in the tree, choosing forms, growing and shrinking structure, and checking the result.
The model holds the rules; this document adds only the steps and the rules that apply in one direction.

## Placing a document

Before writing, decide where the content sits in the tree:

1. State in one or two sentences what the content is and what it covers.
   This statement starts both the overview and the parent's summary.
   If it does not fit in two or three sentences, the content probably holds several topics or kinds.
1. Find the parent document that will introduce it, and plan the summary and link that the parent will carry.
1. Decide whether the content is a part of an existing topic, a new topic in an existing file, or a file of its own.
   Short topics that the same reader needs for the same task stay together in one file, as parts or as topic H2s.
   A topic gets its own file when it serves another reader or task, outgrows its siblings, or needs more than two heading levels.
   A new file goes into its parent's folder, or into the parent's companion folder when the parent is not an index file.
1. Decide each new topic's kind with [document kinds](kinds.md#document-kinds), using the vocabulary in [common uses](uses.md).
1. For a new topic set or a large file, sketch the [topic-by-type review](kinds.md#topic-by-type-review) to see which blocks each subject needs.

## Choosing forms

Start from each block's information type and its [default form](kinds.md#default-forms).
Then adjust with the criteria in [sections, lists, and tables](model.md#sections-lists-and-tables).
When a choice stays unclear, compare with the [examples](examples.md).

The same content can be a part with sections or a list with names.
A short set of parallel options reads best as a list:

```markdown
## Output formats

- **Text**: Groups findings by code and prints fix guidance once per code.
- **JSON**: Lists each finding with its file, lines, code, severity, and message.
```

When each option needs several paragraphs, other documents link to it, or it must appear in the table of contents, it becomes a section:

```markdown
## Output formats

The checker writes text by default and JSON on request.

### Text output

Findings are grouped by code, ...

### JSON output

Each finding is an object with ...
```

## Rules for new writing

Some rules apply only when writing, not when judging existing text:

- **Bold names**: Write names in list items in bold, even though the model accepts other forms.
- **Named references**: Refer to other content by linking to its heading, not by position words such as "above" or "below".
  Use the target's title as the link text where the link introduces it, such as a parent's link to a child.
  Where the sentence already says what the reader will find, a shorter text that still identifies the target is enough.
- **Overviews last**: When the content settles, rewrite the H1 overview and each topic overview to match it.
  If the scope changed, update the parent's summary as well.

## Growing and shrinking

Structure changes as content grows or shrinks, and the promotion ladder in [headings and promotion](model.md#headings-and-promotion) governs both directions.

- **When a list item needs named children**: Promote its name to the heading level the content needs, or remove the names.
- **When a section needs H4**: Move the topic to its own file, placed as [placing a document](#placing-a-document) describes, and leave a summary and link behind.
- **When a topic shrinks to one subsection**: Remove the subsection heading so that the topic becomes a part.
- **When one sibling outgrows the others**: Promote it and leave a summary and a link in its place.
  Alternatively, move only the excess detail to a topic at that level.
- **When a block of another kind or level grows**: Move it to a topic of its own.
  See [blocks of another kind or level](kinds.md#blocks-of-another-kind-or-level).

Restructuring moves content; it does not rewrite it.
Keep the wording of moved content unless the move itself requires a change, such as replacing a position word with a link.

## Checking

The checker reports what a parser can decide or flag, and its findings come with fix guidance.
Use it as follows:

1. Run the checker on the files you created or changed, after the structure is in place.
1. Fix structural findings before sentence-level ones, because structural fixes move sentences.
1. Run the checker once more after fixing, and stop there.
   A warning that remains after judgment is a valid outcome, and the goal is not zero warnings.
1. Run the repository's Markdown linter separately, if it has one, for formatting rules.

Findings apply to what the current task created or made worse.
For example, adding items that push a list past seven makes that warning part of the task.

- **Existing warnings**: Leave them, or reconsider them while giving the existing structure priority.
- **Existing errors**: Fix them inside the section you are editing, and report the rest without fixing them.
- **Requested restructuring**: When the user asks for the structure to be reorganized, apply all findings.
  Run the checker with `--review` to also see information such as oversized sections and links without summaries.

When a structural finding is unclear, read the outline the checker prints for that file.
It shows how each H2 was classified, the deepest list nesting in each section, and how many items carry names in each form.
