# Document kinds and information types

A topic has one document kind, which says what the reader is doing with it.
Each block inside the topic, such as a part, an H3 section, a named list item, or a table, carries one information type.
The kind tells which types dominate a topic, and the type suggests each block's default form.
The structural rules that these choices operate within are in the [document model](model.md).

## Document kinds

The vocabulary of kinds depends on what the documents are for, while information types and default forms stay the same everywhere.

- **Repository documentation**: Judge each topic with the Diátaxis compass, which asks whether the content informs action or cognition, and serves study or work.
  Tutorials and how-to guides have the same dominant type and default form, so they form one kind here: action.
  The remaining kinds are reference and explanation.
- **Project records**: Use record roles as kinds, because a current-state record mixes Diátaxis kinds by nature and a history fits none of them.
  What a record must contain is decided by the project's workflow; this skill decides only its structure.
- **Agent instructions and skills**: Use the repository kinds.
  Workflows are action, rule sets and option lists are reference, and rationale is explanation.
  The entry file of a skill or instruction set is a landing page that introduces its reference documents.

Topic sets have no rule about mixing kinds.
A set may be divided by kind at any level, or by subject with several kinds below.
Each topic still keeps one kind, and each landing page reads as an overview.

Each kind has dominant information types:

| Kind | Dominant types | Types that may accompany them |
| --- | --- | --- |
| Action | Procedure | Principle as a condition, fact as an input |
| Reference | Fact, structure | Principle as a rule |
| Explanation | Concept, principle, process | Structure |

Project records use their roles in the same way:

| Record role | Dominant types | Structure |
| --- | --- | --- |
| Current state | Fact, principle | Named lists by category, linking to history and decisions; rewritten rather than appended to |
| History | Fact, process | Dated headings or items; dates are a mechanical order, so long lists are fine |
| Decision | Principle, concept | The choice and its rationale; alternatives compared in a table; reconsideration conditions as principles |

## Information types

A block carries one of six information types:

| Type | What it conveys |
| --- | --- |
| Procedure | Steps a reader performs to reach a goal |
| Process | What happens over time and who does what |
| Principle | Rules, policies, and guidelines |
| Concept | Ideas and definitions, including how a thing divides into kinds |
| Structure | Parts, functions, and components of a whole |
| Fact | Statements and specifications |

## Default forms

The first step in choosing a block's form is to start from its type:

| Type | Default form |
| --- | --- |
| Procedure | Numbered list with one action per step; a decision table when there are three or more branches |
| Process | Numbered list or paragraphs in time order; a stage-by-actor table when several actors take part |
| Principle | Unordered list with the default rule first and exceptions after it; a decision table for two or more conditions |
| Concept | Definition paragraph saying what the thing is a kind of and what sets it apart, then examples and counterexamples; a list or table that covers every kind exactly once when dividing into kinds |
| Structure | Named list of parts, or a part-by-function table; a nested list or file tree for a hierarchy |
| Fact | Table when the facts share attributes, otherwise a named list or sentences |

The criteria in [sections, lists, and tables](model.md#sections-lists-and-tables) then adjust the default for size and for whether the content is a link target.

## Blocks of another kind or level

When a block whose type does not dominate the topic grows large, judge the block itself with the compass.
When a block goes into much finer or broader detail than its siblings, it belongs to another level.
In either case, move it to a topic of its own kind or level and link to it instead of keeping it inline.
For example, a long conceptual explanation inside a how-to guide becomes an explanation topic that the guide links to.

## Topic-by-type review

A table with subjects as rows and information types as columns shows gaps and misplaced content.
It is an optional review, used at two points rather than on every edit:

- **Planning**: When designing a new topic set or a large file, decide which cells each subject needs and which stay empty on purpose.
- **Review**: When a document seems incomplete, has grown substantially, or is up for structural review, look for empty and misplaced cells.
