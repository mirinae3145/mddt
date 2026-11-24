# Hooks

This document covers the optional hook that keeps agents to this skill's reading and writing procedures.
Read it when installing, configuring, or troubleshooting the hook.
It describes the hook's two behaviors, how to register them in Claude Code and Codex, and their limits.
The implementation is [`scripts/mddt_hook.py`](../scripts/mddt_hook.py), which uses only the Python standard library.

The hook handles `PreToolUse` events and judges each call by its tool.
Its messages start by naming this skill and the path of its `SKILL.md`, so that an agent that has not loaded the skill can find it.
Invalid input or an error inside the hook lets the call proceed, so the hook never blocks work it cannot judge.

## Whole reads

The [reading procedure](reading.md#reading-files-whole) asks agents to read a chosen file whole, yet agents often preview a document with `head` or a line range.
For most files a preview costs only context.
Some files decide what else an agent reads or does, and a cut can hide a link or a requirement there.
The hook denies partial reads of these files, judged by file name without regard to case:

- **READMEs**: Every `README.md`.
  The [document model](model.md#files-and-topics) counts a README as an entry only at the collection root or beside `SKILL.md`, but a hook cannot locate the collection root.
- **Agent entries**: `SKILL.md`, `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md`, the files that tools read by name.
- **Contributor guidance**: `CONTRIBUTING.md`, which is not an entry but decides what a contributor reads before a change.

A Claude Code `Read` call on such a file with `offset` or `limit` is denied, unless its range covers the whole file.
A shell pipeline is denied when `head`, `tail`, `sed -n`, a `sed` quit command, or `awk` with a condition on `NR` reads such a file.
The file can be an argument, an input redirection, or the output of `cat` or `nl` earlier in the pipeline.
The pipeline can also run inside `bash -c` or `sh -c`.
Files over 2,000 lines or 256 KiB pass both, since they cannot be read at once and the reading procedure divides them at topic boundaries.

Whole reads, searches such as `grep` and their cut results, edits such as `sed -i`, writes through `>`, and commands such as `git` that only name a file pass.
A denial tells the agent which file it tried to cut and how to read it whole.
These denials apply in documents that a [`.mddtignore`](ignore-file.md) leaves out as well, since a cut there can still hide a link or a requirement.

## Heading edits

The [writing procedure](writing.md) applies when content is added, moved, or removed, and a change that starts as a sentence fix can grow into new sections.
When a call adds an ATX heading to a Markdown file, the hook lets the call proceed and adds context for the agent.
The context asks the agent to load the skill if it has not, and to follow the writing procedure's placement and checking steps.

The hook compares heading counts outside fenced code before and after the change:

- **Claude Code `Edit`**: The replacement text has more headings than the text it replaces.
- **Claude Code `Write`**: The new content has more headings than the file on disk, or the file is new.
- **Codex `apply_patch`**: The added lines of a Markdown file have more headings than its removed lines.

Renaming a heading or editing text under it adds no heading, so it passes without context.

A document that a [`.mddtignore`](ignore-file.md) leaves out also passes without context, since its collection does not write it to the model.
The hook reads the ignore files from the collection root down to the document's folder, as the checker does.
Like the checker, it takes the nearest folder above the document that holds `.git` as the root.
Without one, it reads the ignore files of every folder above the document, while the checker starts from its working directory.

## Registration

Register the script as a command hook for `PreToolUse` in the host's hook configuration.
Its arguments name the behaviors that a registration runs: `reads` for whole reads and `headings` for heading edits.
Without arguments every behavior runs, and an unknown name is reported on standard error and ignored.

Register each behavior on its own with a matcher for the tools it judges, so that each can be turned on or off separately.
Merge the registrations with existing ones rather than replacing the hook file, and use an interpreter and quoted path suited to the platform.
When an installation manager registers hooks, declare each registration through it instead.

For Claude Code, match `Read` and `Bash` for whole reads and `Edit` and `Write` for heading edits in `settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {"matcher": "Read|Bash", "hooks": [{"type": "command", "command": "python3 /absolute/mddt/skills/mddt/scripts/mddt_hook.py reads", "timeout": 10}]},
      {"matcher": "Edit|Write", "hooks": [{"type": "command", "command": "python3 /absolute/mddt/skills/mddt/scripts/mddt_hook.py headings", "timeout": 10}]}
    ]
  }
}
```

For Codex, match `Bash` for whole reads, since Codex reads files through the shell, and `apply_patch` for heading edits in `hooks.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {"matcher": "^Bash$", "hooks": [{"type": "command", "command": "python3 /absolute/mddt/skills/mddt/scripts/mddt_hook.py reads", "timeout": 10}]},
      {"matcher": "^apply_patch$", "hooks": [{"type": "command", "command": "python3 /absolute/mddt/skills/mddt/scripts/mddt_hook.py headings", "timeout": 10}]}
    ]
  }
}
```

Codex skips a new or changed hook until it is reviewed and trusted, for example through `/hooks`.

## Limits

The hook is a guardrail against habitual partial reads and unplanned structure, not an enforcement boundary:

- **Shell heuristics**: The shell judgment recognizes common command forms only.
  It looks up a file's size from the event's working directory and ignores a `cd` earlier in the command.
  A file name held in a variable, or a partial read through another program such as a Python one-liner, passes.
- **Short previews**: A deliberate preview such as `head -1 README.md` is denied as well, since reading these files whole costs little.
- **Context, not checks**: The heading context reminds the agent of the procedure but cannot tell whether the agent follows it.
  Headings added by shell commands, and Setext headings, are not detected.
- **Ignore files**: A checker run with `--root`, or without a Git root, can read other ignore files than the hook.
  The two can then disagree about whether a document is left out.
- **Codex patches**: The Codex hook documentation does not describe the patch format that the hook reads.
  A change to that format can stop heading detection.
- **Host delivery**: The tests run the script with sample events.
  Claude Code was observed to deny a `Bash` read and to deliver the context of an `Edit`.
  Codex has not been observed yet.
