# Writing and restructuring

This procedure applies the [document model](model.md) when creating a document, adding, moving, or removing content in one, or restructuring a tree.
It covers placing a document in the tree, choosing forms, and rules for new writing.
It also covers growing and shrinking structure, restructuring an existing tree, and checking the result.
This includes preserving link targets and exposing gaps in source material before changing its form.
The model holds the rules, and this document adds only the steps and the rules that apply only when writing.

## Placing a document

Before writing, decide where the content sits in the tree.
When adding to an existing document, place only the added content.
Change the structure around it only where the addition requires it, as [growing and shrinking](#growing-and-shrinking) describes.
When a task creates several documents, choose their entries first and place the other documents from each entry down.
The placement takes these steps:

1. State in one or two sentences what the content is and what it covers.
   This statement starts both the overview and the parent's summary.
   If it does not fit in two or three sentences, the content probably holds several topics or kinds.
1. For a document that needs a parent, find that parent and plan the summary and link it will carry.
   The parent carries the planned summary until the child settles, and then the summary is rewritten as [rules for new writing](#rules-for-new-writing) describe.
   For a new entry, identify how readers will find it, such as through a tool or a collection overview.
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

For existing content, compare the facts and conditions before and after changing its form.
A decision table must expose every case, including cases the source leaves unresolved.
Do not turn a missing case into a policy; ask for the missing decision or mark its outcome as unspecified.

The same content can be a topic with sections or a list with names.
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
  Link text is the exception, because its wording follows its target.
- **Named references**: Refer to other content by linking to its heading, not by position words such as "above" or "below".
  Use the target's title as the link text where the link introduces it, such as a parent's link to a child.
  Where the sentence already says what the reader will find, a shorter text that still identifies the target is enough.
- **Overviews and summaries last**: When the content settles, rewrite the H1 overview and each topic overview to match it.
  Then rewrite the parent's summary of each document whose H1 overview the task wrote or changed, condensing the settled overview, not the planned summary.
  Work up from the deepest changed documents, because a parent's own overview can change once its summaries do.

## Growing and shrinking

Structure changes as content grows or shrinks, and the promotion ladder in [headings and promotion](model.md#headings-and-promotion) governs both directions.

- **When a list item needs named children**: Promote its name to the heading level the content needs, or remove the names.
- **When a section needs H4**: Move the topic to its own file, placed as [placing a document](#placing-a-document) describes, and leave a summary and link behind.
- **When a topic shrinks to one subsection**: Remove the subsection heading so that the topic becomes a part.
- **When one sibling outgrows the others**: Promote it and leave a summary and a link in its place.
  Alternatively, move only the excess detail to a topic at that level.
- **When a block of another kind or level grows**: Move it to a topic of its own, as [blocks of another kind or level](kinds.md#blocks-of-another-kind-or-level) describes.
- **When a change alters what a part or topic answers**: Rewrite that part or topic as a unit from the question it now answers.
  Appending to its end or patching single sentences leaves its old order and form in place.
  Keep its facts, and leave the parts and topics around it as they are.

Moving content does not rewrite it.
Keep the wording of moved content unless the move itself requires a change, such as replacing a position word with a link.
Restructuring alone rewrites only a part or topic whose question the current task changed.
A task can also request content changes, such as adding, removing, correcting, or condensing facts.
A part or topic that receives one may be rewritten as far as that change reaches.

GitHub's generated heading IDs depend on both the heading text and IDs already used in the file.
Reordering or inserting repeated headings can change IDs even when their text stays unchanged.
For example, swapping two sections named `Examples` can exchange which content `#examples` and `#examples-1` identify.
After a move, addition, or removal, compare the affected headings' old and new IDs and update links to preserve their intended content.
A resolving link alone does not prove that it still identifies the same topic.

Moving a heading to another file also changes its path.
Update links to the old path as [links resolve](model.md#links-between-documents) describes.

## Restructuring an existing tree

A requested restructuring, such as bringing a repository's documents to the model for the first time, places existing content again rather than adding new content.
It applies the other steps of this procedure in the following order, so that moves, rewrites, and checks do not undo one another:

1. Read the tree from its entry document, as [choosing files](reading.md#choosing-files) describes, and run the checker on the whole tree with `--review`.
   Keep the findings as a baseline to compare the result with, not as a list of work to clear.
1. Note the question, kind, and reader of each file and topic.
   Also note links into the tree from outside it, such as other repositories or instructions, which the checker cannot see.
1. Design the target tree from the entry document down before moving anything, placing each topic as [placing a document](#placing-a-document) describes.
1. Move files first and headings within files second, updating the links to each moved target.
   Keep the wording of moved content, as [growing and shrinking](#growing-and-shrinking) describes.
1. Rewrite only the parts and topics whose question the new structure changed.
   Then rewrite overviews and parent summaries from the deepest changed documents up, as [rules for new writing](#rules-for-new-writing) describe.
1. Check the result as [checking](#checking) describes for a requested restructuring, running the checker on the whole tree.
   Compare the facts in the old and new documents, so that the moves neither dropped nor duplicated content.

Keep moves and rewrites in separate steps that a reviewer can follow, such as separate commits.
A large tree can be restructured one subtree at a time, from the entry document down.
Report outside links whose targets changed, since updating them lies outside the tree.

## Checking

Checking combines a reread against the model's judgment rules with the checker, which reports what a parser can decide or flag.
Check the result as follows:

1. Once the content has settled, reread each part or topic you changed as a whole.
   Judge whether the changes fit its question, order, and forms, and compare with the [examples](examples.md) where a rule's application is unclear.
   - **Alongside other work**: When the documents change with other work, such as code, the content settles when that work does.
   - **Unchanged rendering**: A part or topic whose changes all leave the rendered document as it was needs no reread.
     Such changes include one-sentence line splits and link target updates after a move, but not a blank line, which splits a paragraph.
   - **Requested content changes**: A part or topic that received a content change the task requested is reread, even when the task otherwise only restructures.
1. Run the checker on the files you created or changed.
   When files or headings are added, removed, moved, or renamed, run it on the whole tree.
   Also check the whole tree when adding or removing an index or companion parent changes document ownership.
   After adding child documents, add `--review` to see links that lack summaries.
   Information findings rest on approximate detection, so judge each one before acting on it.
1. Fix structural findings before sentence-level ones, because structural fixes move sentences.
   Before applying a fix, judge the structure it will produce against the model, including the rules whose warnings it may raise.
   After fixing, reread each fixed part or topic whole.
1. Run the checker once more after fixing, and fix only errors that the fixes introduced.
   If those corrections change files, check them again before stopping.

   Judge a fix by the structure it produces, not by the number of findings.
   Keep a fix that serves the reader better even when it raises another warning, and judge that warning like any other.
   Do not undo a fix only because it raised a warning, or choose one only because it raises none.
   A warning that remains after judgment is a valid outcome, and the goal is not zero warnings.

Findings apply to what the current task created or made worse.
For example, adding items that push a list past seven makes that warning part of the task.
Findings the task did not cause, and requests to restructure, are handled as follows:

- **Existing warnings**: Leave them, or reconsider them while giving the existing structure priority.
- **Existing errors**: Fix them inside the section you are editing, and report the rest without fixing them.
- **Requested restructuring**: When the user asks for the structure to be reorganized, as in [restructuring an existing tree](#restructuring-an-existing-tree), apply all structural findings.
  Apply sentence-level findings as well where the fix leaves the rendered document as it was, such as splitting lines for `line-sentences`.
  Other sentence-level findings need rewriting, so fix them only in parts and topics that [growing and shrinking](#growing-and-shrinking) lets the task rewrite.
  Elsewhere leave them; like other warnings that remain after judgment, they are a valid outcome.

When a structural finding is unclear, read the outline the checker prints for that file.
It shows how each H2 was classified, the deepest list nesting in each section, and how many items carry names in each form.
