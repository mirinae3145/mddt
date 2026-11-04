# Ignore file

A `.mddtignore` file lists the documents that a tree holds but does not write to the model, such as a user's originals or generated material.
The checker skips them, so it neither judges them nor requires them to link into the tree.
This document describes where the file goes, its syntax, and how skipped documents take part in the tree.
Read it when a run should leave out documents that `--exclude` would otherwise have to name each time.

## Placement

Put a `.mddtignore` in the folder whose documents it covers.
The checker opens it directly, so it works whether Git tracks the file, ignores it, or is not used at all.
A file applies to its folder and below, and a deeper file overrides a shallower one.
The files read run from the tree root, or the current directory without a tree root, down to the checked file's folder.

## Syntax

The lines use gitignore syntax, with patterns relative to the folder that holds the file:

- **Lines**: A blank line is skipped, and so is a line starting with `#`.
  A trailing space is dropped unless escaped, and `\#` or `\!` starts a pattern with that character.
- **Negation**: A line starting with `!` un-ignores what an earlier line ignored, though not inside an ignored folder.
- **Folders**: A trailing `/` matches folders only, and everything inside a matched folder is ignored.
- **Anchoring**: A pattern with a `/` before its end matches from the file's folder, and any other pattern matches at any depth.
- **Wildcards**: `*` and `?` stay within one path segment, `[abc]` and `[!abc]` match one character from a set, and `**` as a whole segment matches any number of folders.

The last matching line wins, in the order the files and lines are read.
Other gitignore features, such as a global excludes file or case-insensitive matching, are not supported.

## Skipped documents

A skipped document is reported as skipped, even when it is named as an argument, and `--exclude` patterns add to the ones in the file.
It stays on disk, so it remains part of the tree for the documents that are checked.
Links to it, including their anchors, are still checked, and it still decides whether its children are linked from it.
