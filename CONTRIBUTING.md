# Contributing

This guide covers how the checker is organized and how to verify changes to it.
The skill is meant for any agent and repository, so keep it independent of personal instruction sets, machine paths, and particular workflow tools.

## Checker layout

The checker keeps each kind of content in one place.

- **Detection**: `skills/mddt/scripts/mddt.py` decides what to report and contains no fix guidance.
- **Registry**: `skills/mddt/scripts/rules.toml` holds each code's severity, output group, summary, and rule location.
- **Fix guidance**: `skills/mddt/scripts/fixes.toml` holds the text printed with each code's findings.
  It is one file so that related codes keep consistent wording and option order.

The rule behind each code is marked in the skill's reference documents with a comment such as `<!-- code: list-intro -->` at the end of the rule's line.
Tests check that the registry, fix guidance, and markers name the same codes, and that rule locations and links between skill documents resolve.

Codes are permanent identifiers.
Change a code's severity or wording in the registry instead of renaming it, and add fix guidance with every new code.

The checker reports only what a parser can decide or flag for judgment.
Choices that depend on meaning, such as whether content belongs in a section, list, or table, stay with the writer.

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
