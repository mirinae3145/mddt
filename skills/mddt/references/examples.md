# Examples

These examples show how the judgment rules of the [document model](model.md) apply, mostly as before-and-after pairs.
Read them when it is unclear how a rule applies to the text at hand.

## Structure within a file

These examples show how headings, overviews, and siblings change as content grows inside one file.

### Promotion

A list item whose children need names becomes a heading.

Before:

```markdown
## Configuration

The tool reads its settings from one file.

- **Cache**: Controls where downloads are kept.
  - **Location**: Defaults to the user cache folder.
  - **Size limit**: Defaults to 2 GB.
- **Proxy**: Uses the system proxy unless one is set.
```

After:

```markdown
## Configuration

The tool reads its settings from one file, with separate settings for the cache and the proxy.

### Cache

Cache settings control where downloads are kept.

- **Location**: Defaults to the user cache folder.
- **Size limit**: Defaults to 2 GB.

### Proxy

The tool uses the system proxy unless one is set.
```

"Cache" had named children, so it became an H3, and "Proxy" followed to stay parallel.
The H2 now has H3 children, which makes it a topic with its own overview.
Removing the names from "Location" and "Size limit" would have been an equally valid fix.

### Parts before topics

A file's own parts come before its subtopics.

Before:

```markdown
# Sync tool

The sync tool copies folders between machines and keeps them in step.

## Usage

The tool copies a folder once or watches it for changes.

### Copying a folder
...

### Watching for changes
...

## Requirements

The tool needs Python 3.11 or later.
```

After:

```markdown
# Sync tool

The sync tool copies folders between machines and keeps them in step.

## Requirements

The tool needs Python 3.11 or later.

## Usage

The tool copies a folder once or watches it for changes.

### Copying a folder
...

### Watching for changes
...
```

"Requirements" has no H3, so it is a part of the file's own topic, while "Usage" is a subtopic.

### Level of detail among siblings

A sibling that holds finer detail than the others moves that detail to a topic at its own level.

Before:

```markdown
## Installation

The installation steps differ by operating system.

### Linux
Install the package with your package manager.

### macOS
Install the package with Homebrew.

### Windows
Run the installer.
If the installer stops with error 1603, check the following registry keys ...
(forty more lines of troubleshooting)
```

After:

```markdown
## Installation

The installation steps differ by operating system.

### Linux
Install the package with your package manager.

### macOS
Install the package with Homebrew.

### Windows
Run the installer.
If it stops with an error, see [Windows installer errors](windows-installer-errors.md) for causes and fixes.
```

The troubleshooting was a different level of detail from the installation steps, so it became its own topic.

### Blocks of another kind

A block whose kind differs from its topic's moves to a topic of that kind.

Before:

```markdown
# Restore a backup

Snapshots store each file as blocks, and a block shared by two snapshots is stored once.
(several more paragraphs on how snapshots are stored)

1. Choose the snapshot to restore.
1. Run `sync restore SNAPSHOT TARGET`.
```

After:

```markdown
# Restore a backup

This guide restores a folder from a snapshot.
Restores are fast because snapshots share unchanged blocks, as described in [how snapshots work](snapshots.md).

1. Choose the snapshot to restore.
1. Run `sync restore SNAPSHOT TARGET`.
```

The how-to kept its steps, and the explanation of storage became an explanation topic.

## Lists and tables

These examples show when a list must cover a whole, how nesting carries conditions, and when conditions call for a table.

### Divisions

An introduction that claims a count or a complete set makes the list a division, so the list must match the claim.

Before:

```markdown
The tool supports three storage backends:

- Local folders
- S3-compatible services
- SFTP servers
- WebDAV servers
```

After:

```markdown
The tool supports four storage backends:

- Local folders
- S3-compatible services
- SFTP servers
- WebDAV servers
```

When a set cannot be complete, the claim goes instead of a catch-all item.

Before:

```markdown
Slow syncs have three causes:

- Large files
- Slow networks
- Other causes
```

After:

```markdown
Slow syncs often come from causes such as these:

- Large files
- Slow networks
```

### Details and exceptions in nesting

A detail, condition, or exception that qualifies one item nests under that item.

Before:

```markdown
The tool keeps one photo from each group:

- The photo with the highest resolution is kept.
- With `--prefer PATH`, photos under `PATH` are kept instead.
- If two photos have the same resolution, the older one is kept.
- Under `--prefer PATH`, the resolution rule still decides among those photos.
```

After:

```markdown
The tool keeps one photo from each group:

- **Default**: The photo with the highest resolution is kept.
  - On a tie, the photo with the oldest modification time is kept.
- **Override**: With `--prefer PATH`, photos under `PATH` are kept instead.
  - The default still decides among the photos under `PATH`.
```

Each top-level item now states one rule, and the conditions that only qualify a rule sit under it.
A single nested item is fine, because it marks a detail of its parent rather than a list of its own.

### Decision tables

Conditional content with two or more conditions becomes a decision table.

Before:

```markdown
If the target does not exist, the tool copies the file.
If it exists and is newer, the tool skips it.
If it exists and is older, the tool overwrites it, unless `--keep` is set, in which case it renames the old file first.
```

After:

```markdown
The tool decides what to do with each file as follows:

| Target exists | Target is newer | `--keep` set | Action |
| --- | --- | --- | --- |
| No | — | — | Copy |
| Yes | Yes | — | Skip |
| Yes | No | No | Overwrite |
| Yes | No | Yes | Rename the old file, then copy |
```

The condition columns follow the order of the decision, a dash marks a condition that no longer matters, and each row has one result.

## Links between documents

These examples show how files form a tree and how links outside the tree read.

### Companion folders and downward links

A document gains children in a companion folder beside it, and it links to each child with a summary.

```text
docs/
  README.md
  backends.md
  backends/
    s3.md
    sftp.md
```

In `backends.md`:

```markdown
## Setup pages

Each backend has its own setup page:

- [S3-compatible services](backends/s3.md): bucket permissions and endpoint settings.
- [SFTP servers](backends/sftp.md): key-based login and path mapping.
```

`backends.md` is the parent of the files in `backends/`, and `docs/README.md` is the parent of `backends.md`.
Each summary condenses the child's overview, which stays the canonical version.

### Lateral links

A link outside the tree path says why it is there.

Before:

```markdown
Restores can take a while. See [snapshots](snapshots.md).
```

After:

```markdown
Restores of large folders take longer because every changed block is read again, as described in [how snapshots work](snapshots.md).
```

The sentence now states the relation, so a reader can decide whether to follow the link.
