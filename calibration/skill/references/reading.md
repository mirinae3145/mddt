# Reading a document tree

This procedure uses the guarantees of the [document model](model.md) to find and verify information in a set of Markdown documents.
It covers choosing files, reading them, and handling documents that do not follow the model.

## Choosing files

Explore before reading, starting from the entry document rather than scanning every folder:

1. Read the entry document, such as the README, and follow its downward links toward the subject.
1. Use the folder tree and file names to place each candidate.
1. Judge a candidate by its H1, its overview paragraph, and its list of headings.
1. Use summaries in parent documents only to choose where to go next, and confirm facts in the child document.

## Reading files whole

Read a chosen file whole rather than in fragments.
A conforming file is one topic or a set of related topics, so its boundary is also the boundary of what is relevant.
Fragments lose the context needed to interpret them, such as the H1 overview, the parent topic's own parts, and sibling topics.

When a file is too large to read at once, divide it at topic boundaries rather than at arbitrary lines.
Read the H1 overview and the parent's own parts first, then the topic H2s you need.

## Documents outside the model

External documents, generated files, and long logs do not guarantee this structure.
Search them for the parts you need instead of reading them whole.

## Using the model's guarantees

Each property of the model supports a reading strategy:

| Property | Reading strategy |
| --- | --- |
| Documents are reachable through downward links | Start from the entry document instead of scanning folders |
| Lateral links state why they are there | Follow one when its stated relation, such as evidence or the canonical location, matters to the question |
| The folder tree is the document tree | Find a document's parent and children from where its file sits |
| The H1 and its overview identify a file | Decide from the title and first paragraph whether to read the file, then read it whole |
| Parent summaries condense child overviews | Use summaries to choose a path, and verify facts in the child |
| A topic H2 has H3 children and an overview | Use topic overviews as summaries, and topic boundaries for dividing large files |
| Topics stand alone | Interpret a linked topic as a unit; when a link points to a part, read the topic that owns it |
| A list starts with an introduction, or its heading introduces it | Learn what the list holds, such as decisions, facts, or options, before reading the items |
| Siblings have a comparable level of detail | When a topic does not reach the detail you need, look for a link to that level instead of reading on |
| Only a division claims to cover a whole | Treat a division's items as complete and exclusive, and other lists as possibly partial |
| Conditions and exceptions nest under the item they qualify | Read nested conditions and exceptions before applying the parent item |
| Names appear only on items without named descendants | Use names to find items, but read them in the context of their part |
