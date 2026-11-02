# Contributing

This guide covers how the checker is organized, what to update when a rule changes, how files are licensed, and how to verify changes.
The skill is meant for any agent and repository, so keep it independent of personal instruction sets, machine paths, and particular workflow tools.

## Checker layout

The checker keeps each kind of content in one place.

- **Detection**: `skills/mddt/scripts/mddt.py` decides what to report and contains no fix guidance.
- **Registry**: `skills/mddt/scripts/rules.toml` holds each code's severity, output group, summary, and rule location.
- **Fix guidance**: `skills/mddt/scripts/fixes.toml` holds the text printed with each code's findings.
  It is one file so that related codes keep consistent wording and option order.

The rule behind each code is marked in the skill's reference documents with a comment such as `<!-- code: list-intro -->` at the end of the rule's line.
Tests check that the registry, fix guidance, and markers name the same codes, and that each marker lies inside its rule location.
They also check that links between skill documents resolve.

Codes are permanent identifiers.
Change a code's severity or wording in the registry instead of renaming it, and add fix guidance with every new code.

The checker reports only what a parser can decide or flag for judgment.
Choices that depend on meaning, such as whether content belongs in a section, list, or table, stay with the writer.

## Changing a rule

Each rule is stated once for writers and once for the checker, and a few documents point to those statements.
A change to a rule updates these together:

- **Rule text**: the rule in the skill's reference documents, with its code marker.
- **Checker**: the detection and constants in `mddt.py`, and the code's entries in `rules.toml` and `fixes.toml`.
- **Summaries**: the overview of `model.md`, which `SKILL.md` and README condense, when what the model covers changes.
- **Checker reference**: `references/checker.md`, which README, `SKILL.md`, and `--help` point to, when options, file selection, output, or exit statuses change.

Tests also check that the numbers in `model.md` and in `rules.toml` summaries match the checker's constants, and that the checker reference lists every option.
The calibration material records one past round, so it is not updated when a rule changes.

## Licenses

Every file is covered by a license entry in `REUSE.toml`.
Code and checker data are MIT, documentation is CC BY 4.0, and trivial configuration such as `.gitignore` is CC0.
Place a new file under a covered path, or add it to the matching entry.
Running `reuse lint` from the [REUSE tool](https://reuse.software/) confirms that every file is covered.

## Verification

Run the behavioral checks from the repository root:

```bash
python3 -m unittest discover -s tests -v
```

The tests run the checker through `uv run`, so uv must be installed.
When checking the repository's own documents, exclude the generated material in `calibration/`:

```bash
uv run skills/mddt/scripts/mddt.py --exclude 'calibration/outputs/*' --exclude 'calibration/briefs/*' --exclude 'calibration/skill/*' .
```

Add a test with each new code or behavior change, including a case that must not be reported.
