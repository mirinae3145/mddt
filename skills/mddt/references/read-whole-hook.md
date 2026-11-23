# Read-whole hook

This document covers the optional hook that stops agents from reading certain documents in part.
Read it when installing, configuring, or troubleshooting the hook.
It describes the files the hook covers, how it judges a call, how to register it in Claude Code and Codex, and its limits.
The implementation is [`scripts/read_whole.py`](../scripts/read_whole.py), which uses only the Python standard library.

## Files covered

The [reading procedure](reading.md#reading-files-whole) asks agents to read a chosen file whole, yet agents often preview a document with `head` or a line range.
For most files a preview costs only context.
Some files decide what else an agent reads or does, and a cut can hide a link or a requirement there.
The hook enforces whole reading for these files, judged by file name without regard to case:

- **READMEs**: Every `README.md`.
  The [document model](model.md#files-and-topics) counts a README as an entry only at the collection root or beside `SKILL.md`, but a hook cannot locate the collection root.
- **Agent entries**: `SKILL.md`, `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md`, the files that tools read by name.
- **Contributor guidance**: `CONTRIBUTING.md`, which is not an entry but decides what a contributor reads before a change.

## Judgment

The hook handles `PreToolUse` events and judges two kinds of call:

- **Read calls**: A Claude Code `Read` call on a covered file with `offset` or `limit` is denied, unless its range covers the whole file.
  Files over 2,000 lines or 256 KiB pass, because they cannot be read at once and the reading procedure divides them at topic boundaries.
- **Shell commands**: A pipeline is denied when `head`, `tail`, `sed -n`, a `sed` quit command, or `awk` with `NR` reads a covered file.
  The file can be an argument, an input redirection, or the output of `cat` or `nl` earlier in the pipeline.

Whole reads, searches such as `grep`, edits such as `sed -i`, and commands such as `git` that only name a file pass.
A denial tells the agent which file it tried to cut and how to read it whole.
Invalid input or an error inside the hook lets the call proceed, so the hook never blocks work it cannot judge.

## Registration

Register the script as a command hook for `PreToolUse` in the host's hook configuration.
Merge it with existing registrations rather than replacing the hook file, and use an interpreter and quoted path suited to the platform.
When an installation manager registers hooks, declare the hook through it instead.

For Claude Code, match both the `Read` and `Bash` tools in `settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [{"matcher": "Read|Bash", "hooks": [{"type": "command", "command": "python3 /absolute/mddt/skills/mddt/scripts/read_whole.py", "timeout": 10}]}]
  }
}
```

For Codex, match shell commands in `hooks.json`, since Codex reads files through the shell:

```json
{
  "hooks": {
    "PreToolUse": [{"matcher": "^Bash$", "hooks": [{"type": "command", "command": "python3 /absolute/mddt/skills/mddt/scripts/read_whole.py", "timeout": 10}]}]
  }
}
```

Codex skips a new or changed hook until it is reviewed and trusted, for example through `/hooks`.

## Limits

The hook is a guardrail against habitual partial reads, not an enforcement boundary:

- **Shell heuristics**: The shell judgment recognizes common command forms only.
  A file name held in a variable, or a partial read through another program such as a Python one-liner, passes.
- **Short previews**: A deliberate preview such as `head -1 README.md` is denied as well, since reading these files whole costs little.
- **Host delivery**: The tests run the script with sample events, so they do not show that a host delivers events or honors denials.
  Check one denial in the installed host before relying on the hook.
