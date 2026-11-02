# Document model

This document describes the structure that a conforming Markdown document has.
Writers treat each property as a condition to satisfy, and readers treat it as a guarantee to rely on.
What a topic contains and which form each block takes by default are described in [document kinds and information types](kinds.md).
[Examples](examples.md) show the judgment rules applied to sample text.

## Files and topics

A topic is a unit of meaning that can be read on its own, and a file is a unit of storage.
Each file relates to topics as follows.

- **Topics stand alone**: A topic does not assume that the reader has read what comes before or after it.
  It states its own context and links to named anchors instead of saying "above" or "as described earlier".
- **Files hold topics**: A file is either one topic or a set of topics, never a set of sets.
  As a result, headings stop at H3. <!-- code: heading-depth -->
  Content that needs a fourth level moves to its own file, which the parent links to.
  A file too long to read comfortably at once suggests that its topics have outgrown one file. <!-- code: file-size -->
- **Each file has an identity**: A file has exactly one H1, followed by an overview paragraph. <!-- code: h1-missing, h1-multiple, h1-overview -->
  The overview says what the document is and what it covers, so a reader arriving from anywhere can decide whether to read on.
  Badges and other image-only paragraphs do not count as an overview.
- **File names identify, titles explain**: A file name is read together with the folder tree, while a title must make sense on its own.
  File names are link targets, so keep them short and stable, and keep the name and the title about the same subject.
- **Folders follow the tree**: Where a file sits determines its parent document.
  A folder's index file is the parent of the other documents in that folder and its subfolders.
  It is the first of `SKILL.md`, `README.md`, and `index.md` that the folder holds.
  A file `x.md` is the parent of the documents in a companion folder `x/` beside it, so a document gains children without moving.
  A folder with neither belongs to the parent found the same way one level up.
- **Entry documents**: The root `README.md` and files that tools read by name, such as `SKILL.md` and `AGENTS.md`, are entry documents.
  So is a `README.md` beside a `SKILL.md`, which introduces the folder to people browsing it.
  They need no parent; every other document, including community files such as `CONTRIBUTING.md`, has one.

## Headings and promotion

Each H2 plays one of two roles, and a parser can tell them apart by whether the H2 has H3 children.
The roles and the movement between them work as follows.

- **Topics and parts**: An H2 with H3 children is a topic; an H2 without them is a part of the file's topic.
  A topic H2 has its own overview paragraph before its first H3. <!-- code: topic-overview -->
- **Parts come first**: A parent topic's own parts come before its subtopics. <!-- code: part-after-topic -->
  Roles are inferred from H3 children, so a short subtopic without H3 looks like a part, and ordering findings are therefore only warnings.
- **No skipped levels**: A heading is at most one level below the heading before it. <!-- code: heading-skip -->
- **No section numbers**: Headings carry no section numbers, because levels and titles carry the hierarchy and numbers break when sections move. <!-- code: heading-number -->
  Numbers that belong to the subject, such as versions, dates, and identifiers, stay.
- **Emphasis is not a heading**: A paragraph consisting only of bold or italic text does not stand in for a heading. <!-- code: bold-heading -->
- **Promotion**: A name that would need named children is promoted instead.
  The ladder runs from a leading name in a list item to a heading, then a topic, then a file.
  Promotion goes directly to the level the content needs, and removing the name is an equally valid fix.
- **Demotion**: When content shrinks, the ladder runs the other way. <!-- code: topic-single-child -->
  For example, a topic left with a single H3 can become a part again.

## Paragraphs and sentences

Prose follows these rules about lines, paragraphs, and sentences.

- **One sentence per line**: Each sentence of prose starts on its own line, including in list items. <!-- code: line-sentences -->
  Later sentences of a list item go on indented continuation lines.
  Tools can then find sentence boundaries at line ends instead of guessing at periods in abbreviations, versions, file names, and URLs.
- **Paragraph size**: A paragraph has at most five sentences. <!-- code: paragraph-length, paragraph-run -->
  Four or more paragraphs in a row without a list, table, heading, or code block suggest structure that has not been made visible.
- **Sentence length**: A sentence has at most 25 words, counted as whitespace-separated tokens. <!-- code: sentence-length -->
  A long sentence can usually be split, or holds content that belongs in separate sections.
  A sentence is counted across line breaks until a line ends with sentence punctuation, without code spans, link targets, or URLs.
- **Condition placement**: A condition that decides whether an instruction applies comes before the instruction, so readers it does not concern can skip it.
  An exception to a rule that almost always applies comes after the rule.

## Links between documents

Documents form a tree through links that follow these rules.

- **Downward links**: A parent document links to each of its child documents with a short summary. <!-- code: doc-unlinked, link-without-summary -->
  When a subtopic moves to its own file, its original place keeps that summary and link.
  The summary condenses the child's overview, which remains the canonical version.
  Upward links are needed only when the folder tree does not show where a document belongs.
- **Groups of peer documents**: Sibling topics in separate files are introduced together in one part.
  The part has an introductory sentence followed by a list of links with summaries.
- **Landing pages**: A document that introduces other documents reads as an overview, not as a bare list of links.
- **Anchor targets**: A link to an anchor in another file that expects its target to be read alone points to a topic. <!-- code: anchor-to-part -->
  An anchor to a part only locates content inside a file that the reader reads whole.
- **Lateral links**: A link to a related topic outside the tree path goes in the sentence where the relation matters.
  The sentence shows why the link is there, such as evidence, the canonical location, or further detail.
  A separate list of related documents is optional.
- **Tree before lateral links**: Lateral links do not replace the tree.
  Because every document except an entry document is linked from its parent, every document is reachable through downward links alone.

## Sections, lists, and tables

An information type suggests a default form, as described in [document kinds and information types](kinds.md#default-forms).
The following criteria adjust that default.

- **Section**: Use a section for content that belongs in the table of contents, is a link target, or outgrows a list item.
  Only headings create anchors.
- **List**: Use a list for short, parallel items that are compared side by side.
- **Table**: Use a table when items share attributes.
  A table starts with an introductory sentence under the same rules as a list. <!-- code: table-intro -->
- **Decision table**: Use a decision table for one decision whose outcome depends on two or more combined conditions, or that has three or more outcomes.
  A default rule with nested exceptions and a set of independent rules stay lists.
  Put the condition columns on the left in the order they are decided, and the result column on the right.
  Mark a condition that no longer matters with a dash, cover every combination exactly once, and give each row one result.

## Siblings

Headings at the same level and items in the same list are siblings.
The following rules apply to them.

- **Same level of detail**: Siblings have a comparable level of detail. <!-- code: sibling-imbalance -->
  When one sibling grows much deeper or larger than the others, it probably holds content of another level.
- **Number of sibling sections**: Sibling headings follow the same limit as list items, about seven unless in mechanical order. <!-- code: section-count -->
- **Divisions**: A sibling set is a division when it claims to cover a whole.
  Decision tables, divisions of a concept into kinds, and introductions that state a count or say "one of the following" make that claim.
  A division uses one criterion and covers the whole without gaps or overlaps.
- **Other sets**: Sets that do not claim to cover a whole need neither one criterion nor complete coverage.
  Examples, notes, reasons, procedure steps, and rule collections are usually such sets.
- **Claims only where needed**: A set that does cover a whole still makes the claim only when the reader relies on its completeness.
  A reader relies on it when choosing among all the options or checking that nothing is missing.
  Otherwise the introduction states no count and no completeness, because such a claim has to be kept true whenever the set changes.
- **No false claims**: When a set cannot cover the whole, drop the claim instead of adding a catch-all item.
  Introduce the set with words such as "for example" or "includes", so it is no longer a division.
- **Children answer the parent**: A nested item answers a question that its parent raises, such as how, when, why, or what is excepted.
  This relation is what justifies nesting.

## Lists

Lists carry structure through their introductions, length, nesting, and names.
These rules apply wherever a list appears, under any heading level.

### Introductions

A list starts with an introductory sentence that says what the list contains or which question it answers. <!-- code: list-intro -->
When the list is the only content of a section without subheadings, the section heading introduces it instead.
Continuation paragraphs, code blocks, and nested lists inside items count as part of the list.
This exception does not apply directly under an H1 or a topic H2, which start with an overview paragraph.

Items in one list share a grammatical form.
A top-level list has at least two items, while a single nested item is allowed because it marks a detail or condition of its parent. <!-- code: list-single -->

### Length and order

A list has about seven items or fewer. <!-- code: list-length -->
A list in mechanical order, such as alphabetical, numerical, or date order, can be longer because readers find items without reading their content.
Steps and priorities are ordered by content, so numbered procedures are not exempt.

### Nesting

Lists nest at most three levels, counting ordered and unordered lists alike. <!-- code: list-depth-3, list-depth-4 -->
A fourth level is not allowed, and a third level is allowed but worth reconsidering.
Continuation paragraphs, code blocks, and tables inside an item do not add depth.
Nested items under one parent may play different roles, such as details, conditions, and exceptions, and items with the same role stay together.

### Names

A name is any lead-in that says what an item is about: a bold term, a short phrase followed by a colon, or link text.
Only an item without named descendants carries a name, at every heading level. <!-- code: name-nesting -->
An item whose children need names is promoted as described in [headings and promotion](#headings-and-promotion).

An unnumbered item of several sentences is a block of its own and carries a name where the rule above allows one. <!-- code: item-name, nested-block -->
Where the rule forbids it, a block sits inside another block, which suggests promoting the enclosing item.
A numbered step is labeled by its position and needs no name.
Names within one topic use one form, not counting link text, whose wording follows its target. <!-- code: name-form-mix -->
In a file with topic H2s, each topic H2 is one scope, and the parent's own parts together form another.
