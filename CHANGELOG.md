<!-- markdownlint-disable MD024 -->

# Changelog of MDDT

This file records the changes in each version of the mddt skill, newest first.
The [contributing guide](CONTRIBUTING.md#versions) says what each number of a version means.

## 1.0 &mdash; 2026-11-19

The first version that the skill declares builds on commit [`8d5a104`](https://github.com/mirinae3145/mddt/commit/8d5a104c0d23a86992d2afc8098edea6f2fb7503), the last state without a version.
The entries below are changes from that baseline, whose existing features its documents describe and this file does not list.

### Added

- **Version**: `SKILL.md` declares the skill's version in the `metadata.version` field of its front matter.
- **Output contract**: The checker reference states which parts of the JSON output and exit statuses change only with a new first number.
- **Pinned versions**: The adoption guide pins a version tag instead of a revision, and default-branch jobs print the version they used.
