<!-- markdownlint-disable MD024 -->

# Changelog of MDDT

This file records the changes in each version of the mddt skill, newest first.
The [contributing guide](CONTRIBUTING.md#versions) says what each number of a version means.

## 1.3 &mdash; 2026-11-25

### Changed

- **Editing existing documents**: The writing procedure now asks which documents use the model before editing begins.
  Writers follow established conventions outside that scope and run the checker on new or changed documents the model covers.
- **Preparing a release**: The contributor guide clarifies when a set of changes entering `main` takes a version.
  A contribution keeps the current version while the set is open, even when its major or minor impact is known.

## 1.2 &mdash; 2026-11-24

### Added

- **Checker output**: The hook's new `output` behavior denies shell pipelines that pass the checker's text output through a filter such as `grep`, `head`, or `tail`.
  JSON output, help text, unfiltered runs, and output written to a file pass.
- **Behavior selection**: The hook's arguments name the behaviors a registration runs, `reads`, `headings`, and `output`, and all of them run without arguments.

### Changed

- **Ignored documents**: The hook adds no heading context to documents that a `.mddtignore` leaves out, reading the ignore files as the checker does.
- **Reading the output**: The checking procedure and `SKILL.md` ask agents to read the checker's text output whole, and point scripts that process findings to `--format json`.

## 1.1 &mdash; 2026-11-23

### Added

- **Hook**: `scripts/mddt_hook.py` is an optional `PreToolUse` hook for Claude Code and Codex.
  It denies partial reads of READMEs, agent entries, and contributor guides.
  When an edit adds a heading, it points the agent to the skill and its writing procedure.
  `references/hooks.md` describes its behaviors, its registration, and its limits.

## 1.0 &mdash; 2026-11-19

The first version that the skill declares builds on commit [`8d5a104`](https://github.com/mirinae3145/mddt/commit/8d5a104c0d23a86992d2afc8098edea6f2fb7503), the last state without a version.
The entries below are changes from that baseline, whose existing features its documents describe and this file does not list.

### Added

- **Locked dependencies**: `scripts/mddt.py.lock` fixes the versions of all the checker's dependencies, so that a version of the skill keeps its errors over time.
- **Version**: `SKILL.md` declares the skill's version in the `metadata.version` field of its front matter.
- **Output contract**: The checker reference states which parts of the JSON output and exit statuses change only with a new first number.
- **Pinned versions**: The adoption guide pins a version tag instead of a revision, and default-branch jobs print the version they used.
