# Calibration of the checker's thresholds

This folder keeps the material used to review the checker's numeric thresholds against documents written to the model.
It holds the English inputs and outputs of the third and last calibration round, and the outputs are kept exactly as the writers left them.
The inputs and outputs record that round, so they are not updated when the skill changes.

## Inputs

Each writer was a Claude Sonnet agent at medium effort that received only these inputs:

- **Skill copy**: [The skill copy](skill/SKILL.md) is the skill as it stood when the round ran, without its checker and without the thresholds under review.
  Those thresholds had been set without a measured basis.
  Rules added later, such as making completeness claims only where needed, are missing from the copy.
  Paragraph and sentence length, file size, and sibling size were left to the writer's judgment.
  Limits decided earlier on stated grounds stayed in the copy: about seven list items and sibling headings, headings to H3, and lists to three levels.
- **Brief**: One brief per use lists facts about a fictional subject and leaves the number of files to the writer.
- **Instruction**: Write the documents, then reread them against the skill and revise them, without running any checker.

The briefs cover one fictional subject per use:

- [Repository documentation](briefs/repo-en.md): a command-line tool that finds duplicate photos.
- [Project records](briefs/records-en.md): a lab's migration of microscopy data to object storage.
- [Agent skill](briefs/skill-en.md): a skill for reviewing figures in research manuscripts.

## Outputs

Each output set is the folder one writer produced:

- [Repository documentation](outputs/repo-en/README.md): 14 files.
- [Project records](outputs/records-en/README.md): 8 files.
- [Agent skill](outputs/skill-en/SKILL.md): 14 files.

The outputs are AI-generated test material, not documentation of mddt, and the checker still reports some findings on them.

## Results

[`measure.py`](measure.py) computes each measure's distribution with the checker's own parsing.
It counts whole sentences, as the checker did at the time, not the sentence units that the length checks now use:

```bash
uv run calibration/measure.py calibration/outputs
```

The 95th percentile of each measure compares with the checker's threshold at the time of the round:

| Measure | Median | 95th percentile | Maximum | Threshold at the time |
| --- | --- | --- | --- | --- |
| Sentences per paragraph | 1 | 3 | 5 | More than 5 warns |
| Paragraphs in a row | 1 | 2 | 3 | 4 or more warn |
| Words per sentence | 11 | 23 | 41 | More than 25 warn |
| Section size against the sibling median | 0.89 | 2.2 | 2.83 | 3 times and 20 lines inform (provisional) |
| Sibling headings | 3 | 7 | 7 | More than 7 warn |
| Lines per file | 29 | 63 | 89 | More than 300 inform (provisional) |
| List depth | 1 | 2 | 2 | 3 warns, 4 is an error |

The paragraph and sentence thresholds sit at or above the 95th percentile, so the checker rarely flags writing that follows the model.
The writers knew the sibling heading and list depth limits, so those two rows show compliance with the limits rather than test them.
No file grew large enough to test the file size threshold, and no writer used topic H2s with H3s, so those thresholds stay provisional.

Two earlier rounds used shorter briefs and a skill copy that asked for short paragraphs and sentences, and their material is not kept here.
In all three rounds, Korean writers used fewer whitespace-separated words per sentence than English writers did for the same facts.
Their 95th percentile was 15 to 16 against 23 to 25, so the sentence threshold was reviewed against English only.
