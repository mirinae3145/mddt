# Contributing

This guide covers what to read before a change, how the checker is organized, and what to update when a rule changes.
It also covers how the repository applies the skill to itself, how files are licensed, and how to verify changes.
The skill is meant for any agent and repository, so keep it independent of personal instruction sets, machine paths, and particular workflow tools.

## Before a change

What to read before a change depends on which files it touches:

- **Skill and tests**: A change inside `skills/mddt/` or `tests/` needs the whole repository.
  The rule text, checker, registry, fix guidance, tests, and summaries depend on one another.
  Reading only the touched files can leave them out of step.
  The license texts and the material in `calibration/` beyond its [README](calibration/README.md) can be skipped, since that material records one past round.
- **Repository documents**: A change to another document, such as README or this guide, needs the skill's reference documents.
  The repository's documents follow the model, as [self-conformance](#self-conformance) describes, and the checker covers only part of it.
  The change also needs the documents that the changed text summarizes or that summarize it.
- **Licensing and configuration**: A change to `REUSE.toml`, `LICENSES/`, `.gitignore`, `.mddtignore`, or `.rumdl.toml` needs only this guide.

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

- **Rule text**: the rule in the skill's reference documents, with its code marker, and its entry in `references/terms.md` when the rule defines a term.
- **Checker**: the detection and constants in `mddt.py`, and the code's entries in `rules.toml` and `fixes.toml`.
- **Summaries**: the overview of `model.md`, which `SKILL.md` and README condense, when what the model covers changes.
- **Checker reference**: `references/checker.md`, which README, `SKILL.md`, and `--help` point to, when options, file selection, output, or exit statuses change.

Tests also check that the numbers in `model.md` and in `rules.toml` summaries match the checker's constants, and that the checker reference lists every option.
The calibration material records one past round, so it is not updated when a rule changes.

## Self-conformance

The repository applies the skill to itself on a best-effort basis, aiming for these properties:

- **Model conformance**: The repository's documents follow the document model, including the judgment rules that the checker does not decide.
  Apart from the generated calibration material, they also pass the checker without errors or warnings.
- **Formatting**: The same documents pass the Markdown linter configured in `.rumdl.toml`, which covers formatting that the model leaves out.
- **Checker consistency**: Tests keep the checker's codes, rule locations, numeric limits, and options in step with the reference documents.
- **Self-containment**: The skill folder works without files outside it, since it holds the checker's specification and an index of terms.

## Licenses

Every file is covered by a license entry in `REUSE.toml`.
Code and checker data are MIT, documentation is CC BY 4.0, and trivial configuration such as `.gitignore`, `.mddtignore`, and `.rumdl.toml` is CC0.
Place a new file under a covered path, or add it to the matching entry.
Running `reuse lint` from the [REUSE tool](https://reuse.software/) confirms that every file is covered.

## Verification

A change is verified by the tests, and a change to the repository's documents also by checking them against the model and linting them.
Each command exits with a nonzero status when its check fails, so a CI job can run it unchanged.

### Tests

Run the behavioral checks from the repository root:

```bash
python3 -m unittest discover -s tests -v
```

The tests run the checker through `uv run`, so uv must be installed.
Add a test with each new code or behavior change, including a case that must not be reported.

After changing `mddt.py`, also run the tests with coverage to find the lines and branches they never reach:

```bash
MDDT_COVERAGE=1 python3 -m unittest discover -s tests
uvx coverage combine
uvx coverage report -m
```

The coverage run starts the checker through coverage rather than as the documentation tells users to, so it does not replace the plain run.
Its report supports judgment rather than setting a target, so it has no required percentage.
Unreached lines in the code the change added or modified are judged as follows:

- **Specified behavior**: A line that decides a finding, file selection, output, or exit status needs a test.
  Specified behavior is what the model, the checker reference, or a comment in the checker states.
- **Unspecified conditions**: A line that guards against another platform, a broken registry, or a similar unspecified condition can stay unreached.

### Documents

The repository's own documents follow the model, as [self-conformance](#self-conformance) describes.
Changes to them follow the skill's [writing procedure](skills/mddt/references/writing.md) at both ends.
Before writing, place new content as [placing a document](skills/mddt/references/writing.md#placing-a-document) describes.

Once the content settles, reread each changed part or topic whole against the model's judgment rules.
These include divisions, levels of detail among siblings, and summaries in parent documents.
Where a rule's application is unclear, compare with the [examples](skills/mddt/references/examples.md).

Then run the checker from the repository root, which decides only the rules a parser can see:

```bash
uv run skills/mddt/scripts/mddt.py .
```

The tracked `.mddtignore` leaves out the generated material in `calibration/`.
Self-conformance aims for no warnings.
A change that keeps one reports it with the reason in its commit message or pull request.

Finally, lint the documents with the pinned version of [rumdl](https://github.com/rvben/rumdl):

```bash
uvx rumdl@0.3.2 check .
```

`.rumdl.toml` turns off the line length rule, since each sentence has its own line, and fixes the list and emphasis markers in use.
It also leaves out the generated calibration material.
`uvx rumdl@0.3.2 fmt .` fixes most formatting findings automatically.
Update the pinned version in a change of its own, because new rules can report findings in unchanged documents.
