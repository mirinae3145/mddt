# Contributing

This guide covers how the checker is organized and how to verify changes to it.
The skill is meant for any agent and repository, so keep it independent of personal instruction sets, machine paths, and particular workflow tools.

## Checker layout

The checker keeps each kind of content in one place.

- **Detection**: `skills/mddt/scripts/mddt.py` decides what to report and contains no fix guidance.
- **Registry**: `skills/mddt/scripts/rules.toml` holds each code's severity, output group, summary, and rule location.
- **Fix guidance**: `skills/mddt/scripts/fixes.toml` holds the text printed with each code's findings.
  It is one file so that related codes keep consistent wording and option order.

Codes are permanent identifiers.
Change a code's severity or wording in the registry instead of renaming it, and add fix guidance with every new code.

The checker reports only what a parser can decide or flag for judgment.
Choices that depend on meaning, such as whether content belongs in a section, list, or table, stay with the writer.

## Verification

Run the behavioral checks from the repository root:

```bash
python3 -m unittest discover -s tests -v
```

The tests run the checker through `uv run`, so uv must be installed.
Add a test with each new code or behavior change, including a case that must not be reported.
