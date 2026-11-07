# SPDX-FileCopyrightText: 2026 Taeha Shin
# SPDX-License-Identifier: MIT
"""Behavioral checks through the checker's command-line interface."""
import ast
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/mddt/scripts'
SCRIPT = SCRIPTS / 'mddt.py'
# Pinned with the coverage commands in CONTRIBUTING.md and the CI workflow.
COVERAGE = 'coverage==7.17.2'


def run(*args, cwd=None, env=None, uv='uv'):
    """Run the checker as a user would, optionally under coverage measurement.

    With MDDT_COVERAGE set, each run appends branch coverage data to
    .coverage.* files at the repository root, which `coverage combine` merges.
    The dependencies still come from the script's inline metadata.
    """
    if os.environ.get('MDDT_COVERAGE'):
        command = [uv, 'run', '--quiet', '--with', COVERAGE, '--with-requirements', str(SCRIPT),
                   'python', '-m', 'coverage', 'run', '--branch', '--parallel-mode',
                   f'--data-file={ROOT / ".coverage"}', f'--include={SCRIPT}', str(SCRIPT)]
    else:
        command = [uv, 'run', '--quiet', str(SCRIPT)]
    return subprocess.run([*command, *args], capture_output=True, text=True, cwd=cwd, env=env)


class CheckerCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, text):
        path = self.dir / name
        path.write_text(text, encoding='utf-8')
        return path

    def codes(self, text, name='doc.md'):
        path = self.write(name, text)
        result = run('--format', 'json', str(path))
        self.assertIn(result.returncode, (0, 1), result.stderr)
        return [(d['code'], d['line']) for d in json.loads(result.stdout)['diagnostics']]

    def review(self, text):
        path = self.write('doc.md', text)
        result = run('--format', 'json', '--review', str(path))
        return [d['code'] for d in json.loads(result.stdout)['diagnostics'] if d['severity'] == 'info']

    def assertCodes(self, text, expected):
        self.assertEqual(sorted(c for c, _ in self.codes(text)), sorted(expected))


class FileAndHeadingRules(CheckerCase):
    def test_conforming_topic_set_has_no_findings(self):
        self.assertCodes(
            '# Title\n\nOverview.\n\n## Part\n\nText.\n\n'
            '## Topic\n\nTopic overview.\n\n### One\n\nA.\n\n### Two\n\nB.\n', [])

    def test_missing_and_multiple_h1(self):
        self.assertCodes('## Only part\n\nText.\n', ['h1-missing'])
        self.assertCodes('# A\n\nOverview.\n\n# B\n\nOverview.\n', ['h1-multiple'])

    def test_h1_overview_ignores_badges_and_comments(self):
        badge = '[![b](x.svg)](https://example.com/y)'
        self.assertCodes(f'# T\n\n{badge}\n\n<!-- note -->\n\nOverview.\n', [])
        self.assertCodes(f'# T\n\n{badge}\n\n## Part\n\nText.\n', ['h1-overview'])
        self.assertCodes('# T\n\n```\ncode\n```\n', ['h1-overview'])
        badges = '[![a](a.svg)](https://example.com/x) [![b](b.svg)](https://example.com/y)\n![c](c.svg)'
        self.assertCodes(f'# T\n\n{badges}\n\nOverview.\n', [])
        self.assertCodes(f'# T\n\n{badges}\n\n## Part\n\nText.\n', ['h1-overview'])

    def test_heading_skip_and_depth(self):
        self.assertCodes('# T\n\nOverview.\n\n### Deep\n\nText.\n', ['heading-skip'])
        self.assertCodes(
            '# T\n\nOverview.\n\n## Topic\n\nOverview.\n\n### A\n\nX.\n\n#### B\n\nY.\n\n### C\n\nZ.\n',
            ['heading-depth'])

    def test_section_numbers_in_sequence(self):
        self.assertCodes('# T\n\nOverview.\n\n## 1. Start\n\nA.\n\n## 2. Next\n\nB.\n', ['heading-number'])
        self.assertCodes('# T\n\nOverview.\n\n## A. Start\n\nA.\n\n## B. Next\n\nB.\n', ['heading-number'])
        self.assertCodes('# T\n\nOverview.\n\n## III. Start\n\nA.\n\n## IV. Next\n\nB.\n', ['heading-number'])
        self.assertCodes('# T\n\nOverview.\n\n## 2.0 migration\n\nA.\n\n## 3.0 migration\n\nB.\n', [])
        self.assertCodes('# T\n\nOverview.\n\n## 2026-10-30 review\n\nA.\n\n## 2026-10-31 review\n\nB.\n', [])
        self.assertCodes('# T\n\nOverview.\n\n## 3 things to know\n\nA.\n\n## Other\n\nB.\n', [])

    def test_subject_numbers_in_headings_stay(self):
        for first, second in [('2025 review', '2026 review'), ('1.4 (2026-01-10)', '1.5 (2026-02-01)'),
                              ('1.4 release notes', '1.5 release notes'), ('2 players', '3 players')]:
            self.assertCodes(f'# T\n\nOverview.\n\n## {first}\n\nA.\n\n## {second}\n\nB.\n', [])
        self.assertCodes('# T\n\nOverview.\n\n## 1.4 (2026-01)\n\nOverview.\n\n'
                         '### 1.4.1 (2026-01-10)\n\nA.\n\n### 1.4.2 (2026-02-01)\n\nB.\n', [])

    def test_subsection_numbers_extending_the_parent(self):
        self.assertCodes('# T\n\nOverview.\n\n## 2. Scope\n\nOverview.\n\n### 2.1 Inputs\n\nA.\n\n### 2.2 Outputs\n\nB.\n',
                         ['heading-number'])
        self.assertCodes('# T\n\nOverview.\n\n## Scope\n\nOverview.\n\n### 1.1. Inputs\n\nA.\n\n### 1.2. Outputs\n\nB.\n',
                         ['heading-number'])

    def test_topic_overview(self):
        self.assertCodes(
            '# T\n\nOverview.\n\n## Topic\n\n### A\n\nX.\n\n### B\n\nY.\n', ['topic-overview'])

    def test_part_after_topic_is_reported_once_per_run(self):
        found = self.codes(
            '# T\n\nOverview.\n\n## Topic\n\nOverview.\n\n### A\n\nX.\n\n### B\n\nY.\n\n'
            '## Late one\n\nText.\n\n## Late two\n\nText.\n')
        self.assertEqual(found, [('part-after-topic', 17)])

    def test_part_after_topic_unless_mechanically_ordered(self):
        def history(titles, topic):
            return '# T\n\nOverview.\n\n' + ''.join(
                f'## {t}\n\nOverview.\n\n### A\n\nX.\n\n### B\n\nY.\n\n' if t == topic else f'## {t}\n\nText.\n\n'
                for t in titles)
        dated = ['Release, 2026-10-30', 'Pin check, 2026-10-28', 'Build, 2026-10-21', 'Plan, 2026-10-19']
        self.assertCodes(history(dated, dated[1]), [])
        self.assertCodes(history(list(reversed(dated)), dated[2]), [])
        undated = dated[:3] + ['Plan']
        self.assertCodes(history(undated, dated[1]), ['part-after-topic'])
        shuffled = [dated[0], dated[2], dated[1], dated[3]]
        self.assertCodes(history(shuffled, dated[2]), ['part-after-topic'])
        # Two titles always sort in one direction, so they show no order.
        self.assertCodes(history(['Zeta', 'Alpha'], 'Zeta'), ['part-after-topic'])
        # Name order does not count, since a few titles fall into it by chance.
        self.assertCodes(history(['Gamma', 'Beta', 'Alpha'], 'Beta'), ['part-after-topic'])
        self.assertCodes(history(['4. Ship', '3. Run', '2. Build', '1. Plan'], '3. Run'), [])
        # Parts before the first topic break no rule, so they are left out of
        # the order.
        self.assertCodes(history(['Records'] + dated, dated[1]), [])
        self.assertCodes(history(['Records'] + shuffled, dated[2]), ['part-after-topic'])
        # Only the H2s under one H1 are compared, so an ordered set under
        # another H1 does not exempt them.
        self.assertCodes(history(shuffled, dated[2]) + history(dated, dated[1]),
                         ['h1-multiple', 'part-after-topic'])

    def test_topic_single_child(self):
        self.assertCodes(
            '# T\n\nOverview.\n\n## Topic\n\nOverview.\n\n### Only\n\nX.\n', ['topic-single-child'])

    def test_readme_closing_sections_may_follow_topics(self):
        body = '# Tool\n\nOverview.\n\n## Usage\n\nOverview.\n\n### Copy\n\nCopy files.\n\n### Watch\n\nWatch files.\n\n'
        for title in ('License', 'Licenses', 'Licence', 'Licences', 'Copyright',
                      'Acknowledgments', 'Acknowledgements', 'Credits', 'Citation', 'Citing',
                      'AI disclosure', 'Contributing', '**LICENSE**', 'AI   disclosure'):
            with self.subTest(title=title):
                self.assertEqual(self.codes(body + f'## {title}\n\nNotice.\n', 'README.md'), [])
        closing = '## Contributing\n\nSend patches.\n\n## License\n\nMIT.\n\n## AI disclosure\n\nAI assisted.\n'
        self.assertEqual(self.codes(body + closing, 'readme.MD'), [])
        (self.dir / 'docs').mkdir()
        self.assertEqual(self.codes(body + closing, 'docs/README.md'), [])

    def test_readme_closing_exception_keeps_other_ordering_findings(self):
        body = '# Tool\n\nOverview.\n\n## Usage\n\nOverview.\n\n### Copy\n\nCopy files.\n\n### Watch\n\nWatch files.\n\n'
        license = '## License\n\nMIT.\n\n'
        for name, tail, line in (
                ('guide.md', license, 17),
                ('README.extra.md', license, 17),
                ('README.md', '## Requirements\n\nPython.\n\n' + license, 17),
                ('README.md', license + '## Requirements\n\nPython.\n', 17),
                ('README.md', license + '## Configuration\n\nOverview.\n\n### Cache\n\nLocal.\n\n### Proxy\n\nNone.\n', 17),
                ('README.md', '## License configuration\n\nSettings.\n', 17),
                ('README.md', '## License and credits\n\nNotice.\n', 17),
                ('README.md', '## 라이선스\n\nMIT.\n', 17)):
            with self.subTest(name=name, tail=tail):
                self.assertEqual(self.codes(body + tail, name), [('part-after-topic', line)])
        # The closing group does not hide or count toward earlier late parts.
        path = self.write('README.md', body + '## Requirements\n\nPython.\n\n' + license)
        data = json.loads(run('--format', 'json', str(path)).stdout)
        self.assertTrue(data['diagnostics'][0]['message'].endswith('part "Requirements" follows topic "Usage"'))

    def test_readme_closing_sections_keep_roles_and_other_checks(self):
        self.assertEqual(self.codes('## License\n\nMIT.\n', 'README.md'), [('h1-missing', 1)])
        self.assertEqual(self.codes('', 'README.md'), [('h1-missing', 1)])
        body = '# Tool\n\nOverview.\n\n## Usage\n\nOverview.\n\n### Copy\n\nCopy files.\n\n### Watch\n\nWatch files.\n\n'
        closing = '## License\n\nMIT.\n\n## Credits\n\n### Authors\n\nNames.\n\n## AI disclosure\n\nAI assisted.\n'
        self.assertEqual(self.codes(body + closing, 'README.md'),
                         [('topic-overview', 21), ('topic-single-child', 21)])
        path = self.write('README.md', body + '## License\n\nSee [terms](missing.txt).\n')
        data = json.loads(run('--format', 'json', '--outline', str(path)).stdout)
        self.assertEqual([d['code'] for d in data['diagnostics']], ['link-broken'])
        self.assertIn('H2 License  [3 lines; part]', '\n'.join(data['outlines'][str(path)]))
        # A new H1 ends the earlier document; only the file's closing group is exempt.
        self.assertEqual(self.codes(body + '## License\n\nMIT.\n\n# Other\n\nOverview.\n', 'README.md'),
                         [('h1-multiple', 21), ('part-after-topic', 17)])

    def test_readme_closing_sections_do_not_break_date_order(self):
        body = ('# Tool\n\nOverview.\n\n## Release 2026-11-03\n\nOverview.\n\n'
                '### Added\n\nFeature.\n\n### Fixed\n\nBug.\n\n'
                '## Release 2026-11-02\n\nText.\n\n## Release 2026-11-01\n\nText.\n\n')
        self.assertEqual(self.codes(body + '## License\n\nMIT.\n', 'README.md'), [])
        shuffled = body.replace('2026-11-01', '2026-11-04')
        self.assertEqual(self.codes(shuffled + '## License\n\nMIT.\n', 'README.md'), [('part-after-topic', 17)])

    def test_bold_paragraph_used_as_heading(self):
        self.assertCodes('# T\n\nOverview.\n\n**Pseudo heading**\n\nText.\n', ['bold-heading'])
        self.assertCodes('# T\n\nOverview.\n\n**A bold sentence.**\n\nText.\n', [])


class ListRules(CheckerCase):
    def test_list_intro_requires_paragraph(self):
        self.assertCodes('# T\n\nOverview.\n\n| a |\n| - |\n| b |\n\n- x\n- y\n', ['list-intro'])
        self.assertCodes('# T\n\nOverview.\n\nThe list:\n\n- x\n- y\n', [])

    def test_table_intro_follows_list_rules(self):
        table = '| a | b |\n| - | - |\n| 1 | 2 |\n'
        self.assertCodes(f'# T\n\nOverview.\n\n```\ncode\n```\n\n{table}', ['table-intro'])
        self.assertCodes(f'# T\n\nOverview.\n\nThe values:\n\n{table}', [])
        self.assertCodes(f'# T\n\nOverview.\n\n## Values\n\n{table}', [])

    def test_sole_list_in_part_needs_no_intro(self):
        self.assertCodes('# T\n\nOverview.\n\n## Items\n\n- x\n  - detail\n  - more\n- y\n', [])
        self.assertCodes('# T\n\nOverview.\n\n## Items\n\n- x\n- y\n\n<!-- note -->\n', [])

    def test_heading_may_introduce_a_block_that_paragraphs_follow(self):
        table = '| a | b |\n| - | - |\n| 1 | 2 |\n'
        self.assertCodes('# T\n\nOverview.\n\n## Items\n\n- x\n- y\n\nAfter.\n', ['heading-intro'])
        self.assertCodes(f'# T\n\nOverview.\n\n## Topic\n\nOverview.\n\n### Values\n\n{table}\nAfter.\n\n### B\n\nY.\n',
                         ['heading-intro'])
        self.assertCodes('# T\n\nOverview.\n\n## Items\n\n- x\n- y\n\nMore:\n\n- z\n- w\n', ['heading-intro'])
        self.assertCodes('# T\n\nOverview.\n\n## Topic\n\n- x\n- y\n\nAfter.\n\n### A\n\nX.\n\n### B\n\nY.\n',
                         ['topic-overview'])
        path = self.write('warn.md', '# T\n\nOverview.\n\n## Items\n\n- x\n- y\n\nAfter.\n')
        self.assertEqual(run(str(path)).returncode, 0)

    def test_heading_does_not_introduce_a_block_followed_by_other_blocks(self):
        table = '| a | b |\n| - | - |\n| 1 | 2 |\n'
        found = self.write('doc.md', '# T\n\nOverview.\n\n## Steps\n\n1. Run it.\n1. Check it.\n\n```\ncode\n```\n')
        data = json.loads(run('--format', 'json', str(found)).stdout)
        self.assertEqual([d['message'] for d in data['diagnostics']],
                         ['list does not start with an introductory paragraph: '
                          'list follows the heading and precedes a code block'])
        self.assertCodes('# T\n\nOverview.\n\n## Items\n\n- x\n- y\n\n1. a\n1. b\n', ['list-intro', 'list-intro'])
        self.assertCodes(f'# T\n\nOverview.\n\n## Items\n\n{table}\n- x\n- y\n', ['table-intro', 'list-intro'])
        self.assertCodes('# T\n\nOverview.\n\n## Items\n\n- x\n- y\n\n**Pseudo heading**\n\nText.\n',
                         ['list-intro', 'bold-heading'])

    def test_list_right_after_h1_is_an_overview_problem_only(self):
        self.assertCodes('# T\n\n- x\n- y\n', ['h1-overview'])

    def test_list_depth(self):
        three = '# T\n\nOverview.\n\nList:\n\n- a\n  - b\n    - c\n    - d\n  - e\n- f\n'
        self.assertCodes(three, ['list-depth-3'])
        four = '# T\n\nOverview.\n\nList:\n\n- a\n  - b\n    - c\n      - d\n      - e\n    - f\n  - g\n- h\n'
        self.assertCodes(four, ['list-depth-4'])

    def test_single_item_list(self):
        self.assertCodes('# T\n\nOverview.\n\nList:\n\n- only\n', ['list-single'])

    def test_single_nested_item_marks_a_detail(self):
        self.assertCodes('# T\n\nOverview.\n\nList:\n\n- a\n  - detail of a\n- b\n', [])

    def test_long_list_unless_mechanically_ordered(self):
        unordered = '\n'.join(f'- {w}' for w in 'pear apple fig kiwi plum lime date cherry'.split())
        self.assertCodes(f'# T\n\nOverview.\n\nFruit:\n\n{unordered}\n', ['list-length'])
        ordered = '\n'.join(f'- {w}' for w in sorted('pear apple fig kiwi plum lime date cherry'.split()))
        self.assertCodes(f'# T\n\nOverview.\n\nFruit:\n\n{ordered}\n', [])
        dates = '\n'.join(f'- 2026-10-{d:02d}: entry' for d in range(20, 10, -1))
        self.assertCodes(f'# T\n\nOverview.\n\nLog:\n\n{dates}\n', [])
        versions = '\n'.join(f'- {v} release' for v in ['1.2', '1.9', '1.10', '1.11', '2.0', '2.1', '2.10', '3.0'])
        self.assertCodes(f'# T\n\nOverview.\n\nReleases:\n\n{versions}\n', [])
        trailing = '\n'.join(f'- {w} review, 2026-10-{d:02d}' for w, d in zip('pear apple fig kiwi plum lime date cherry'.split(), [3, 3, 5, 8, 12, 21, 21, 29]))
        self.assertCodes(f'# T\n\nOverview.\n\nLog:\n\n{trailing}\n', [])
        shuffled = '\n'.join(f'- {w} review, 2026-10-{d:02d}' for w, d in zip('pear apple fig kiwi plum lime date cherry'.split(), [3, 12, 5, 8, 3, 21, 21, 29]))
        self.assertCodes(f'# T\n\nOverview.\n\nLog:\n\n{shuffled}\n', ['list-length'])

    def test_named_item_with_named_descendant(self):
        self.assertCodes(
            '# T\n\nOverview.\n\nList:\n\n- **Outer**: text\n  - **Inner**: text\n  - plain\n- **Other**: x\n',
            ['name-nesting'])
        self.assertCodes(
            '# T\n\nOverview.\n\nList:\n\n- **Outer**: text\n  - Inner: text\n  - plain\n- **Other**: x\n',
            ['name-nesting', 'name-form-mix'])
        self.assertCodes(
            '# T\n\nOverview.\n\nList:\n\n- **Outer**: text\n  - plain\n    - **Deep**: text\n    - plain\n'
            '  - plain\n- **Other**: x\n',
            ['name-nesting', 'list-depth-3'])

    def test_items_of_several_sentences_are_blocks(self):
        long = 'First sentence.\n  Second sentence.'
        self.assertEqual(self.review(f'# T\n\nOverview.\n\nList:\n\n- {long}\n- short\n'), ['item-name'])
        self.assertEqual(self.review(f'# T\n\nOverview.\n\nSteps:\n\n1. {long}\n1. short\n'), [])
        self.assertEqual(self.review(f'# T\n\nOverview.\n\nList:\n\n- **Name**: {long}\n- **Other**: x\n'), [])
        nested = f'# T\n\nOverview.\n\nList:\n\n- **Name**: rule.\n  - {long}\n  - short\n- **Other**: x\n'
        self.assertEqual(self.review(nested), ['nested-block'])
        holder = f'# T\n\nOverview.\n\nList:\n\n- {long}\n  - **Name**: x\n  - **Other**: y\n- short\n'
        self.assertEqual(self.review(holder), ['nested-block'])

    def test_numbered_steps_are_not_blocks_or_names(self):
        long = 'First sentence.\n   Second sentence.'
        holder = f'# T\n\nOverview.\n\nSteps:\n\n1. {long}\n   - **Name**: x\n   - **Other**: y\n1. short\n'
        self.assertEqual(self.review(holder), [])
        inside = '# T\n\nOverview.\n\nList:\n\n- **Name**: rule.\n  1. First sentence.\n     Second sentence.\n  1. short\n- **Other**: x\n'
        self.assertEqual(self.review(inside), [])
        labeled = '# T\n\nOverview.\n\nSteps:\n\n1. **Settings** opens.\n   - First sentence.\n     Second sentence.\n   - short\n1. Close it.\n'
        self.assertEqual(self.review(labeled), ['item-name'])
        self.assertCodes('# T\n\nOverview.\n\nScope:\n\n- In: x\n- Out: y\n\n'
                         'Steps:\n\n1. **Settings** 메뉴를 연다.\n1. **Save**를 누른다.\n', [])

    def test_name_forms_are_compared_per_topic(self):
        text = ('# T\n\nOverview.\n\n## Topic A\n\nOverview.\n\n### One\n\nList:\n\n- **a**: x\n- **b**: y\n\n'
                '### Two\n\nList:\n\n- c: x\n- d: y\n\n'
                '## Topic B\n\nOverview.\n\n### Three\n\nList:\n\n- e: x\n- f: y\n\n### Four\n\nText.\n')
        self.assertEqual(self.codes(text), [('name-form-mix', 20)])

    def test_step_ending_in_colon_is_not_a_name(self):
        self.assertCodes(
            '# T\n\nOverview.\n\nList:\n\n- **A**: x\n- Install the tool with pipx:\n\n  ```sh\n  pipx install t\n  ```\n- **B**: y\n', [])

    def test_colon_inside_code_does_not_end_a_name(self):
        self.assertCodes('# T\n\nOverview.\n\nList:\n\n- `C0: 접속 및 코멘트 확인용.` 설명.\n- **B**: y\n- **C**: z\n', [])
        self.assertCodes('# T\n\nOverview.\n\nList:\n\n- `--root`: sets the root.\n- **B**: y\n', ['name-form-mix'])

    def test_link_names_do_not_count_as_a_form(self):
        self.write('a.md', '# A\n\nOverview.\n')
        self.write('b.md', '# B\n\nOverview.\n')
        self.assertCodes(
            '# T\n\nOverview.\n\n## Docs\n\n- [A](a.md): what A covers.\n- [B](b.md): what B covers.\n\n'
            '## Scope\n\n- **In**: x\n- **Out**: y\n', [])

    def test_prose_starting_with_link_or_time_is_not_a_name(self):
        self.assertCodes(
            '# T\n\nOverview.\n\nList:\n\n- **A**: x\n'
            '  - [Spec](https://example.com/u)을 확인했다.\n  - Meet at 10:30 today.\n- **B**: y\n', [])


    def test_a_name_broken_across_lines_keeps_its_form(self):
        self.assertCodes('# T\n\nOptions:\n\n- **Alpha\n  beta**: First.\n- **Gamma**: Second.\n', [])

    def test_empty_items_give_a_list_no_mechanical_order(self):
        words = ['Alpha', 'Beta', 'Delta', 'Echo', 'Golf', 'Hotel', 'India', 'Juliet']
        items = ''.join(f'- {word}\n' for word in words)
        self.assertCodes(f'# T\n\nWords:\n\n{items}', [])
        self.assertCodes(f'# T\n\nWords:\n\n{items}-\n', ['list-length'])


class ProseRules(CheckerCase):
    def test_paragraph_length_counts_lines(self):
        five = ''.join(f'Sentence {n}.\n' for n in range(5))
        self.assertCodes(f'# T\n\n{five}', [])
        self.assertCodes(f'# T\n\n{five}One more.\n', ['paragraph-length'])

    def test_paragraph_run(self):
        three = 'One.\n\nTwo.\n\nThree.\n'
        self.assertCodes(f'# T\n\n{three}', [])
        self.assertCodes(f'# T\n\n{three}\nFour.\n', ['paragraph-run'])
        self.assertCodes(f'# T\n\n{three}\nList:\n\n- a\n- b\n\nAfter.\n', ['paragraph-run'])

    def test_sentence_length_spans_line_breaks_but_not_code(self):
        words = ' '.join(['word'] * 13)
        self.assertCodes(f'# T\n\n{words}\n{words}.\n', ['sentence-length'])
        self.assertCodes(f'# T\n\n{words} `a b c d e f g h`\n{words[:-5]}.\n', [])

    def test_words_are_whitespace_tokens_without_entities(self):
        words = ' '.join(['이름'] * 13)
        self.assertCodes(f'# T\n\n{words} &rightarrow; {words[:-3]}.\n', [])
        self.assertCodes(f'# T\n\n{words} &rightarrow; {words}.\n', ['sentence-length'])

    def test_hard_wrapped_sentences_end_inside_lines(self):
        words = ' '.join(['word'] * 10)
        self.assertCodes(f'# T\n\n{words}. Next {words}\nand {words}.\n', ['line-sentences'])

    def test_line_sentences(self):
        self.assertCodes('# T\n\nFirst sentence. Second sentence.\n', ['line-sentences'])
        self.assertCodes('# T\n\n첫 문장이다. 둘째 문장이다.\n', ['line-sentences'])
        self.assertCodes('# T\n\nUse a tool, e.g. Python, with version 1.2 here.\n', [])
        self.assertCodes('# T\n\nSee `a.b` and [Spec. One](https://example.com/u) now.\n', [])
        self.assertCodes('# T\n\n보관함을 스캔한다. `tool scan PATH`\n', [])
        self.assertCodes('# T\n\nAsk the U.S. Office and call foo. bar handles it.\n', [])


class SentenceUnits(CheckerCase):
    LEFT = 'The worker reads every input file from the local folder before it starts the scheduled validation process'
    RIGHT = 'it writes the complete results to the selected output directory after all checks finish successfully'

    def findings(self, texts, *options):
        paths = [self.write(f'case{n}.md', f'# T\n\n{text}\n') for n, text in enumerate(texts)]
        result = run('--format', 'json', *options, *map(str, paths))
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        return [[d for d in data['diagnostics'] if d['file'] == str(p)] for p in paths]

    def test_punctuation_linked_clauses_have_separate_word_limits(self):
        separators = ['; ', ': ', ':', ' — ', ' – ', '—', ' &mdash; ', ' &ndash; ',
                      ' &#8212; ', ' &#x2014; ', '&semi; ', '&colon; ', ';\n', ':\n', ' —\n']
        texts = [f'{self.LEFT}{sep}{self.RIGHT}.' for sep in separators]
        self.assertEqual(self.findings(texts), [[] for _ in texts])

    def test_paragraph_limit_counts_the_same_units_as_the_word_limit(self):
        clauses = ['The build failed', 'the tests stopped', 'the job ended',
                   'the logs vanished', 'the worker crashed', 'the queue stalled']
        five = '; '.join(clauses[:5]) + '.'
        six = '; '.join(clauses) + '.'
        found = self.findings([five, six, six.replace('; ', ';\n'), six.replace('; ', '.\n')])
        self.assertEqual(found[0], [])
        for result in found[1:]:
            self.assertEqual([d['code'] for d in result], ['paragraph-length'])
            self.assertIn('paragraph has 6 sentence units', result[0]['message'])

    def test_conjunctions_without_strong_punctuation_keep_one_unit(self):
        texts = [f'{self.LEFT}{sep}{self.RIGHT}.' for sep in (' and ', ', and ', ', but ', ', so ')]
        for result in self.findings(texts):
            self.assertEqual([d['code'] for d in result], ['sentence-length'])
            self.assertIn('sentence unit has 33 words', result[0]['message'])

    def test_complete_clauses_can_start_with_a_condition(self):
        left = 'When the cache is warm, the worker reads each file before starting the validation process'
        self.assertEqual(self.findings([f'{left}; {self.RIGHT}.']), [[]])

    def test_enumeration_and_fragments_do_not_create_length_boundaries(self):
        cases = [
            ('The tool accepts these values',
             'red, green, blue, yellow, orange, purple, white, black, gray, cyan, magenta, '
             'brown, pink, gold, silver, beige, teal, ivory, indigo, and violet'),
            (self.LEFT, 'a complete and detailed report of every result for every input'),
            (self.LEFT, 'if the service receives every input before the scheduled validation process'),
            (self.LEFT, 'when the service receives every input before the scheduled validation process'),
            (self.LEFT, 'to write every result to the output folder after the checks finish'),
        ]
        texts = [f'{left}{sep}{right}.' for left, right in cases for sep in (': ', ':\n', '; ', ' — ')]
        for result in self.findings(texts):
            self.assertEqual([d['code'] for d in result], ['sentence-length'])

    def test_inserted_phrases_and_bracketed_clauses_stay_with_the_sentence(self):
        texts = [
            'The worker—a small Python module maintained by our team—reads every input file '
            'from the local folder before it starts the scheduled validation process for all configured projects every single morning.',
            'The worker (the build failed; the tests stopped) reads every input file '
            'from the local folder before it starts the scheduled validation process for all configured projects every single morning.',
        ]
        for result in self.findings(texts):
            self.assertEqual([d['code'] for d in result], ['sentence-length'])

    def test_enumeration_with_words_that_can_be_verbs_is_not_a_clause(self):
        text = ('Limits decided earlier on stated grounds stayed in the copy: '
                'about seven list items and sibling headings, headings to H3, and lists to three levels in total.')
        found = self.findings([text])[0]
        self.assertEqual([d['code'] for d in found], ['sentence-length'])
        self.assertIn('sentence unit has 27 words', found[0]['message'])

    def test_long_second_unit_reports_its_source_line(self):
        right = f'{self.RIGHT} and keeps every previous result in a separate directory for later review'
        texts = [f'The build failed; {right}.', f'The build failed;\n{right}.',
                 f'The build failed:\n{right}.', f'The build failed &mdash;\n  {right}.']
        for result, line in zip(self.findings(texts), (3, 4, 4, 4)):
            self.assertEqual([(d['code'], d['line']) for d in result], [('sentence-length', line)])
            self.assertIn('sentence unit has 27 words', result[0]['message'])

    def test_code_links_and_entities_do_not_create_spurious_boundaries(self):
        texts = [
            f'{self.LEFT} `; {self.RIGHT}`.',
            f'{self.LEFT} https://example.com/a;b:c.',
            f'{self.LEFT} &rightarrow; {self.RIGHT}.',
            f'[{self.LEFT}; {self.RIGHT}](https://example.com).',
            f'{self.LEFT} <!-- ; {self.RIGHT} -->.',
            f'`worker` reads every file before the scheduled validation process; {self.RIGHT}.',
            f'{self.LEFT}; `worker` writes every result after the checks finish successfully.',
        ]
        found = self.findings(texts)
        self.assertEqual([[d['code'] for d in ds] for ds in found],
                         [[], [], ['sentence-length'], ['sentence-length'], [], [], []])

    def test_imperatives_split_but_other_scripts_keep_existing_boundaries(self):
        imperative = ('Read every input file from the local folder before starting the scheduled validation process; '
                      'write every result to the output folder after finishing the scheduled validation process.')
        korean = ' '.join(['이름'] * 13) + '; ' + ' '.join(['이름'] * 13) + '.'
        found = self.findings([imperative, korean])
        self.assertEqual(found[0], [])
        self.assertEqual([d['code'] for d in found[1]], ['sentence-length'])

    def test_length_units_do_not_change_line_layout_or_list_item_naming(self):
        text = '# T\n\nOverview.\n\nSteps:\n\n- The build failed; the tests stopped.\n- Restart the worker.\n'
        self.assertEqual(self.review(text), [])
        self.assertCodes(text, [])
        self.assertCodes(text.replace('; the', '. The'), ['line-sentences'])

    def test_list_item_labels_are_not_separate_units(self):
        for label in ('**Parts come first**:', '__Parts come first__:', 'Parts come first:',
                      '[Parts come first](https://example.com):'):
            with self.subTest(label=label):
                self.assertCodes('# T\n\nOverview.\n\nRules:\n\n'
                                 f'- {label} The build failed.\n  The tests stopped.\n  The job ended.\n'
                                 '  The worker crashed.\n  The queue stalled.\n- Other.\n', [])

    def test_missing_model_is_an_explicit_usage_error(self):
        # A deliberately unavailable model exercises the actual CLI error path
        # without uninstalling the model or changing the user's environment.
        self.write('en_core_web_md.py', 'raise ImportError("model unavailable")\n')
        path = self.write('doc.md', '# T\n\nThe build failed; the tests stopped.\n')
        result = run('--format', 'json', str(path), env={**os.environ, 'PYTHONPATH': str(self.dir)})
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, '')
        self.assertIn('cannot load the English sentence model', result.stderr)
        # Ordinary prose does not load a model it does not need.
        path.write_text('# T\n\nThe build failed.\n', encoding='utf-8')
        result = run('--format', 'json', str(path), env={**os.environ, 'PYTHONPATH': str(self.dir)})
        self.assertEqual(result.returncode, 0, result.stderr)


class TreeRules(CheckerCase):
    def tree(self, files, *options):
        for name, text in files.items():
            path = self.dir / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding='utf-8')
        result = run('--format', 'json', *options, str(self.dir))
        data = json.loads(result.stdout)
        return sorted((Path(d['file']).relative_to(self.dir).as_posix(), d['code'])
                      for d in data['diagnostics'])

    def test_parent_must_link_to_child(self):
        found = self.tree({
            'README.md': '# R\n\nSee [A](a.md).\n',
            'a.md': '# A\n\nOverview.\n',
            'b.md': '# B\n\nOverview.\n',
        })
        self.assertEqual(found, [('b.md', 'doc-unlinked')])

    def test_git_root_decides_parents_of_a_checked_subfolder(self):
        (self.dir / '.git').mkdir()
        (self.dir / 'sub').mkdir()
        self.write('README.md', '# R\n\nOverview.\n')
        self.write('sub/a.md', '# A\n\nOverview.\n')
        data = json.loads(run('--format', 'json', str(self.dir / 'sub')).stdout)
        self.assertEqual([d['code'] for d in data['diagnostics']], ['doc-unlinked'])

    def test_companion_folder_and_folder_index(self):
        found = self.tree({
            'README.md': '# R\n\nSee [A](a.md) and [docs](docs/).\n',
            'a.md': '# A\n\nSee [C](a/c.md), [B](b.md).\n',
            'b.md': '# B\n\nOverview.\n',
            'a/c.md': '# C\n\nOverview.\n',
            'a/d.md': '# D\n\nOverview.\n',
            'docs/README.md': '# Docs\n\nSee [E](sub/e.md).\n',
            'docs/sub/e.md': '# E\n\nOverview.\n',
        })
        self.assertEqual(found, [('a/d.md', 'doc-unlinked'), ('b.md', 'doc-unlinked')])

    def test_entry_documents_need_no_parent(self):
        found = self.tree({
            'README.md': '# R\n\nOverview.\n',
            'skills/x/SKILL.md': '# X\n\nSee [ref](references/r.md).\n',
            'skills/x/references/r.md': '# Ref\n\nOverview.\n',
        })
        self.assertEqual(found, [])

    def test_skill_file_outranks_readme_beside_it(self):
        found = self.tree({
            'README.md': '# R\n\nOverview.\n',
            'skills/x/SKILL.md': '# X\n\nSee [guide](references/guide.md).\n',
            'skills/x/README.md': '# X for people\n\nOverview.\n',
            'skills/x/references/guide.md': '# Guide\n\nOverview.\n',
        })
        self.assertEqual(found, [])

    def test_exclude_skips_non_documents(self):
        found = self.tree({
            'README.md': '# R\n\nOverview.\n',
            'templates/case.md': 'no heading\n',
        })
        self.assertEqual(found, [('templates/case.md', 'doc-unlinked'), ('templates/case.md', 'h1-missing')])
        data = json.loads(run('--format', 'json', '--root', str(self.dir), '--exclude', 'templates/*',
                              str(self.dir)).stdout)
        self.assertEqual(data['diagnostics'], [])

    def test_anchor_to_part_is_review_information(self):
        files = {
            'README.md': '# R\n\nSee [part](other.md#part), [topic](other.md#topic), [file](other.md), [own](#r).\n',
            'other.md': '# O\n\nOverview.\n\n## Part\n\nText.\n\n## Topic\n\nOverview.\n\n### A\n\nX.\n\n### B\n\nY.\n',
        }
        self.assertEqual(self.tree(files), [])
        self.assertEqual(self.tree(files, '--review'), [('README.md', 'anchor-to-part')])

    def link_findings(self, files, *options):
        return [(name, code) for name, code in self.tree(files, *options)
                if code in ('link-broken', 'anchor-missing')]

    def test_links_to_missing_paths_are_errors(self):
        (self.dir / 'docs').mkdir()
        (self.dir / 'pic.png').write_bytes(b'')
        links = ['a.md', 'docs/', 'pic.png', 'my%20file.md', '<my file.md>', '한글.md', 'a.md?plain=1',
                 'https://example.com/none.md', 'mailto:a@example.com', '/no/such/file.md', '//host/none.md']
        text = '# R\n\nLinks:\n\n' + ''.join(f'- [link]({href})\n' for href in links)
        found = self.tree({
            'README.md': text + '\nSee [gone](gone.md),\n[folder](none/), and\n[image](none.png).\n',
            'a.md': '# A\n\nOverview.\n',
            'my file.md': '# M\n\nOverview.\n',
            '한글.md': '# H\n\nOverview.\n',
        })
        self.assertEqual([f for f in found if f[1] == 'link-broken'], [('README.md', 'link-broken')] * 3)
        data = json.loads(run('--format', 'json', str(self.dir / 'README.md')).stdout)
        self.assertEqual([d['line'] for d in data['diagnostics'] if d['code'] == 'link-broken'],
                         [len(links) + 6, len(links) + 7, len(links) + 8])

    def test_anchors_must_match_a_heading(self):
        found = self.link_findings({
            'README.md': '# R\n\nOverview.\n\n## Own part\n\nLinks:\n\n'
                         '- [own](#own-part), [own missing](#gone)\n'
                         '- [topic](a.md#topic), [repeated](a.md#topic-1), [encoded](a.md#%EC%86%8C%EA%B0%9C)\n'
                         '- [dot](a.md#문서자동화의-배치), [html](a.md#custom), [empty](a.md#)\n'
                         '- [missing](a.md#nope), [line](a.md#L10), [source](a.md?plain=1#L10)\n'
                         '- [line](script.py#L10), [folder](docs/#intro)\n',
            'a.md': '# A\n\nOverview.\n\n## Topic\n\nText.\n\n## Topic\n\nText.\n\n'
                    '## 소개\n\nText.\n\n## 문서·자동화의 배치\n\nText.\n\n<a id="custom"></a>\nText.\n',
            'script.py': 'pass\n',
            'docs/README.md': '# Docs\n\nOverview.\n\n## Intro\n\nText.\n',
        })
        self.assertEqual(found, [('README.md', 'anchor-missing')] * 3)

    def github_repo(self, origin):
        if shutil.which('git') is None:
            self.skipTest('git is not installed')
        git = ['git', '-C', str(self.dir)]
        subprocess.run(['git', 'init', '--quiet', '-b', 'main', str(self.dir)], check=True)
        subprocess.run([*git, '-c', 'user.name=t', '-c', 'user.email=t@example.com',
                        'commit', '--quiet', '--allow-empty', '-m', 'init'], check=True)
        if origin:
            subprocess.run([*git, 'remote', 'add', 'origin', origin], check=True)
            subprocess.run([*git, 'update-ref', 'refs/remotes/origin/fix/x', 'HEAD'], check=True)

    def test_github_links_to_the_own_repository_resolve(self):
        self.github_repo('git@github.com:Owner/Pkg.git')
        web = 'https://github.com/owner/pkg'
        found = self.tree({
            'README.md': '# R\n\nOverview.\n\n## Links\n\nPages:\n\n'
                         f'- [Contributing]({web}/blob/main/CONTRIBUTING.md): how to contribute.\n'
                         f'- [Docs]({web}/tree/main/docs/): the documentation.\n'
                         f'- [Branch]({web}/blob/fix/x/CONTRIBUTING.md#setup), [gone]({web}/blob/main/gone.md)\n'
                         f'- [anchor]({web}/blob/main/CONTRIBUTING.md#nope), [commit]({web}/blob/1a2b3c4/old.md)\n'
                         '- [other](https://github.com/owner/other/blob/main/none.md), '
                         f'[raw](https://raw.githubusercontent.com/owner/pkg/main/none.md)\n',
            'CONTRIBUTING.md': '# Contributing\n\nOverview.\n\n## Setup\n\nText.\n',
            'docs/README.md': '# Docs\n\nOverview.\n',
        })
        # The web links place CONTRIBUTING.md and docs/ in the tree, so neither is unlinked.
        self.assertEqual([f for f in found if f[1] in ('link-broken', 'anchor-missing', 'doc-unlinked')],
                         [('README.md', 'anchor-missing'), ('README.md', 'link-broken')])

    def test_github_links_without_a_github_origin_are_left_alone(self):
        for origin in (None, 'https://gitlab.com/owner/pkg.git'):
            with self.subTest(origin=origin):
                shutil.rmtree(self.dir)
                self.dir.mkdir()
                self.github_repo(origin)
                found = self.tree({
                    'README.md': '# R\n\nSee [the guide](https://github.com/owner/pkg/blob/main/CONTRIBUTING.md).\n',
                    'CONTRIBUTING.md': '# Contributing\n\nOverview.\n',
                })
                self.assertEqual(found, [('CONTRIBUTING.md', 'doc-unlinked')])

    def test_links_with_only_a_query_are_left_alone(self):
        self.assertEqual(self.link_findings({'README.md': '# R\n\nOpen [the source](?plain=1).\n'}), [])

    def test_unreadable_documents_are_skipped_as_link_targets_and_parents(self):
        (self.dir / 'README.md').write_bytes(b'# R\n\n\xff\n')
        (self.dir / 'b.md').write_bytes(b'# B\n\n\xff\n')
        doc = self.write('a.md', '# A\n\nSee [B](b.md#part).\n')
        result = run('--format', 'json', '--root', str(self.dir), str(doc))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['diagnostics'], [])

    def test_math_is_not_read_as_links(self):
        found = self.link_findings({
            'README.md': '# R\n\nThe ratio $[A](z,t)/[A]_0$ falls.\n\n$$\n[A](z,T) = 1\n$$\n\nSee [gone](gone.md).\n',
        })
        self.assertEqual(found, [('README.md', 'link-broken')])

    def test_linked_trees_are_checked_for_existence_only(self):
        tree, other = self.dir / 'tree', self.dir / 'other'
        other.mkdir()
        (other / 'doc.md').write_text('# Other\n\nOverview.\n', encoding='utf-8')
        tree.mkdir()
        (tree / 'linked').symlink_to(other)
        (tree / 'dangling').symlink_to(self.dir / 'none')
        (tree / 'README.md').write_text(
            '# R\n\nLinks:\n\n- [anchor](linked/doc.md#nope)\n- [missing](linked/none.md)\n'
            '- [dangling](dangling/doc.md)\n', encoding='utf-8')
        data = json.loads(run('--format', 'json', '--root', str(tree), str(tree)).stdout)
        self.assertEqual([(d['code'], d['line']) for d in data['diagnostics']],
                         [('link-broken', 6), ('link-broken', 7)])

    def test_link_without_summary(self):
        found = self.tree({
            'README.md': '# R\n\nChildren:\n\n- [A](a.md)\n- [B](b.md): what B covers.\n',
            'a.md': '# A\n\nOverview.\n',
            'b.md': '# B\n\nSee [A](a.md).\n',
        }, '--review')
        self.assertEqual(found, [('README.md', 'link-without-summary')])

    def test_one_summarized_link_is_enough(self):
        found = self.tree({
            'README.md': '# R\n\nChildren:\n\n- [A](a.md)\n- [A](a.md): what A covers.\n',
            'a.md': '# A\n\nOverview.\n',
        }, '--review')
        self.assertEqual(found, [])

    def test_section_count_unless_mechanically_ordered(self):
        sections = ''.join(f'## {w}\n\nText.\n\n' for w in 'pear apple fig kiwi plum lime date cherry'.split())
        self.assertEqual(self.tree({'README.md': f'# T\n\nOverview.\n\n{sections}'}), [('README.md', 'section-count')])
        dated = ''.join(f'## 2026-10-{d:02d}\n\nText.\n\n' for d in range(20, 10, -1))
        self.assertEqual(self.tree({'README.md': f'# T\n\nOverview.\n\n{dated}'}), [])
        titles = ['RC5 Registry 공개, 2026-10-29', 'Pin 확인, 2026-10-21~22', 'Build, 2026-10-21', 'Plan, 2026-10-19',
                  'Board, 2026-10-02~03', 'Kickoff, 2026-09-30', 'Order, 2026-09-30', 'Idea, 2026-09-01']
        ending = ''.join(f'## {t}\n\nText.\n\n' for t in titles)
        self.assertEqual(self.tree({'README.md': f'# T\n\nOverview.\n\n{ending}'}), [])
        undated = ''.join(f'## {t}\n\nText.\n\n' for t in titles[:-1] + ['Idea'])
        self.assertEqual(self.tree({'README.md': f'# T\n\nOverview.\n\n{undated}'}), [('README.md', 'section-count')])

    def test_sibling_imbalance_and_file_size(self):
        big = ''.join(f'Line {n}.\n\n' for n in range(30))
        text = f'# T\n\nOverview.\n\n## A\n\nShort.\n\n## B\n\n{big}## C\n\nShort.\n'
        found = self.tree({'README.md': text}, '--review')
        self.assertIn(('README.md', 'sibling-imbalance'), found)
        pair = f'# T\n\nOverview.\n\n## A\n\nShort.\n\n## B\n\n{big}'
        self.assertNotIn(('README.md', 'sibling-imbalance'), self.tree({'README.md': pair}, '--review'))
        long = '# T\n\nOverview.\n\n' + ''.join(f'- item {n}\n' for n in range(400))
        found = self.tree({'README.md': long}, '--review')
        self.assertIn(('README.md', 'file-size'), found)


class Changelogs(CheckerCase):
    def inspect(self, text, name='CHANGELOG.md', *options):
        path = self.write(name, text)
        result = run('--format', 'json', '--review', *options, str(path))
        self.assertIn(result.returncode, (0, 1), result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data['files'], [str(path)])
        self.assertEqual(data['skipped'], [])
        return data

    def test_conventional_releases_need_no_overviews_or_list_introductions(self):
        text = ('# Changelog\n\n## Unreleased\n\n### Fixed\n\n- Fixed a crash.\n\n'
                'A note about the fix.\n\n```\nexample\n```\n\n- Added a check.\n\n'
                '## 1.0\n\n- First release.\n')
        for name in ('CHANGELOG.md', 'changelog.en.md', 'ChAnGeLoG.MD', 'CHANGELOG'):
            with self.subTest(name=name):
                data = self.inspect(text, name)
                self.assertEqual(data['diagnostics'], [])
                outline = '\n'.join(data['outlines'][str(self.dir / name)])
                self.assertNotRegex(outline, r'overview|; topic|; part')
                self.assertIn('H3 Fixed', outline)
                self.assertIn('list depth 1', outline)

    def test_other_names_keep_ordinary_document_rules(self):
        for name in ('changes.md', 'changelog-extra.md', 'my-changelog.md'):
            with self.subTest(name=name):
                data = self.inspect('# Changelog\n\n## Version\n\n- Change.\n', name)
                self.assertEqual({d['code'] for d in data['diagnostics']}, {'h1-overview', 'list-single'})

    def test_h1_heading_steps_and_emphasized_headings_remain_checked(self):
        cases = [
            ('## Version\n\n- Change.\n', {'h1-missing'}),
            ('# Changelog\n\n# Extra\n', {'h1-multiple'}),
            ('# Changelog\n\n### Fixed\n\n- Change.\n', {'heading-skip'}),
            ('# Changelog\n\n**Fixed**\n\n- Change.\n', {'bold-heading'}),
        ]
        for text, expected in cases:
            with self.subTest(text=text):
                data = self.inspect(text)
                self.assertEqual({d['code'] for d in data['diagnostics']}, expected)
        self.assertEqual(run(str(self.dir / 'CHANGELOG.md')).returncode, 1)

    def test_deep_and_numbered_headings_keep_their_convention(self):
        text = ('# Changelog\n\n## 1. Current\n\n### Fixed\n\n#### Parser\n\n- Change.\n\n'
                '## 2. Previous\n\n- Change.\n')
        self.assertEqual(self.inspect(text)['diagnostics'], [])

    def test_release_growth_does_not_trigger_counts_or_sizes(self):
        labels = 'pear apple fig kiwi plum lime date cherry'.split()
        changes = ''.join(f'- Updated {label}.\n' for label in labels)
        text = '# Changelog\n\n' + ''.join(f'## {label}\n\n- Change.\n\n' for label in labels)
        text += '## Large release\n\n### Fixed\n\n' + changes * 40
        self.assertEqual(self.inspect(text)['diagnostics'], [])

    def test_list_nesting_and_names_remain_checked(self):
        cases = [
            ('- a\n  - b\n    - c\n', {'list-depth-3'}),
            ('- a\n  - b\n    - c\n      - d\n', {'list-depth-4'}),
            ('- **Outer**: text\n  - **Inner**: text\n', {'name-nesting'}),
            ('- **One**: text\n- Two: text\n', {'name-form-mix'}),
            ('- First sentence.\n  Second sentence.\n', {'item-name'}),
            ('- **Outer**: text\n  - First sentence.\n    Second sentence.\n', {'nested-block'}),
        ]
        for body, expected in cases:
            with self.subTest(body=body):
                data = self.inspect('# Changelog\n\n## Unreleased\n\n' + body)
                self.assertEqual({d['code'] for d in data['diagnostics']}, expected)

    def test_name_forms_are_scoped_to_each_release_without_categories(self):
        text = '# Changelog\n\n## Unreleased\n\n- **One**: text\n\n## 1.0\n\n- Two: text\n'
        self.assertEqual(self.inspect(text)['diagnostics'], [])

    def test_prose_remains_checked(self):
        cases = [
            ('- First sentence. Second sentence.\n', {'line-sentences', 'item-name'}),
            ('- ' + ' '.join(['word'] * 26) + '.\n', {'sentence-length'}),
            ('- ' + '\n  '.join(f'Sentence {n}.' for n in range(6)) + '\n',
             {'paragraph-length', 'item-name'}),
            ('One.\n\nTwo.\n\nThree.\n\nFour.\n', {'paragraph-run'}),
        ]
        for body, expected in cases:
            with self.subTest(body=body):
                data = self.inspect('# Changelog\n\n## Unreleased\n\n' + body)
                self.assertEqual({d['code'] for d in data['diagnostics']}, expected)

    def test_table_introductions_remain_checked_at_every_heading_level(self):
        table = '| Old | New |\n| --- | --- |\n| a | b |\n\n'
        for level in range(1, 7):
            heading = '# Changelog\n\n' + ''.join(
                '#' * n + f' Section {n}\n\n' for n in range(2, level + 1))
            tails = ['']
            if level < 6:
                tails.append('\n' + '#' * (level + 1) + ' Details\n\n- Change.\n')
            for tail in tails:
                for suffix, leaf_codes in (('', set()), ('Notes.\n', {'heading-intro'}),
                                           ('```\nexample\n```\n', {'table-intro'})):
                    with self.subTest(level=level, tail=tail, suffix=suffix):
                        # Only a leaf section below H1 can introduce its table.
                        expected = {'table-intro'} if level == 1 or tail else leaf_codes
                        data = self.inspect(heading + table + suffix + tail)
                        self.assertEqual({d['code'] for d in data['diagnostics']}, expected)
                        introduced = heading + 'The changed values are:\n\n' + table + suffix + tail
                        self.assertEqual(self.inspect(introduced)['diagnostics'], [])

    def test_link_checks_depend_on_the_target_not_the_source(self):
        self.write('guide.md', '# Guide\n\nOverview.\n\n## Detail\n\nText.\n')
        self.write('changelog.old.md', '# History\n\n## 1.0\n\n### Fixed\n\n- Change.\n')
        data = self.inspect('# Changelog\n\n## Unreleased\n\n'
                            '- See [guide](guide.md#detail).\n'
                            '- See [history](changelog.old.md#fixed).\n'
                            '- See [missing anchor](changelog.old.md#gone).\n'
                            '- See [missing file](gone.md).\n'
                            '- See [own section](#unreleased).\n')
        self.assertEqual({d['code'] for d in data['diagnostics']},
                         {'anchor-to-part', 'anchor-missing', 'link-broken'})
        incoming = self.inspect('# Guide\n\nSee [release](CHANGELOG.md#unreleased) and '
                                '[category](changelog.old.md#fixed).\n', 'guide.md')
        self.assertEqual(incoming['diagnostics'], [])

    def test_parent_links_and_child_summaries_remain_checked(self):
        self.write('README.md', '# Project\n\nOverview.\n')
        (self.dir / 'CHANGELOG').mkdir()
        self.write('CHANGELOG/details.md', '# Details\n\nOverview.\n')
        text = '# Changelog\n\n## Unreleased\n\n- [Details](CHANGELOG/details.md)\n'
        data = self.inspect(text, 'CHANGELOG.md', '--root', str(self.dir))
        self.assertEqual({d['code'] for d in data['diagnostics']}, {'doc-unlinked', 'link-without-summary'})
        self.write('README.md', '# Project\n\nSee [history](CHANGELOG.md).\n')
        data = self.inspect(text.replace('details.md)', 'details.md): the change details.'),
                            'CHANGELOG.md', '--root', str(self.dir))
        self.assertEqual(data['diagnostics'], [])

    def test_changelogs_can_still_be_explicitly_excluded(self):
        path = self.write('CHANGELOG.md', 'no title\n')
        for options in (('--exclude', 'CHANGELOG.*'), ()):
            if not options:
                self.write('.mddtignore', 'CHANGELOG.md\n')
            result = run('--format', 'json', '--root', str(self.dir), *options, str(path))
            data = json.loads(result.stdout)
            self.assertEqual((data['files'], data['skipped'], data['diagnostics']), ([], [str(path)], []))


class Interface(CheckerCase):
    def test_exit_codes(self):
        ok = self.write('ok.md', '# T\n\nOverview.\n')
        warn = self.write('warn.md', '# T\n\nOverview.\n\nList:\n\n- a\n  - b\n    - c\n    - d\n  - e\n- f\n')
        bad = self.write('bad.md', '# T\n')
        self.assertEqual(run(str(ok)).returncode, 0)
        self.assertEqual(run(str(warn)).returncode, 0)
        self.assertEqual(run(str(bad)).returncode, 1)
        self.assertEqual(run(str(self.dir / 'missing.md')).returncode, 2)
        latin = self.dir / 'latin.md'
        latin.write_bytes('# Caf\u00e9\n\nOverview.\n'.encode('latin-1'))
        self.assertEqual(run(str(latin)).returncode, 2)

    def test_text_output_groups_locations_and_prints_fix_once(self):
        a = self.write('a.md', '# A\n')
        b = self.write('b.md', '# B\n')
        out = run(str(a), str(b)).stdout
        self.assertEqual(out.count('error h1-overview:'), 1)
        self.assertEqual(out.count('  fix:'), 1)
        self.assertIn(f'{a}:1', out)
        self.assertIn(f'{b}:1', out)

    def test_text_output_counts_info_and_long_skip_lists(self):
        mixed = self.write('mixed.md', '# T\n\n- First sentence.\n  Second sentence.\n- short\n')
        out = run('--review', str(mixed)).stdout
        self.assertIn('1 error(s), 0 warning(s), 1 info in 1 file(s)', out)
        self.assertEqual(out.count('  fix:'), 2)
        for n in range(6):
            self.write(f'skip{n}.md', '# S\n\nOverview.\n')
        out = run('--exclude', 'skip*', str(self.dir)).stdout
        self.assertIn('skipped: 6 files', out)

    def test_rule_locations_name_the_skill_folder_as_run(self):
        doc = self.write('bad.md', '# T\n')
        linked, copied = self.dir / 'linked', self.dir / 'copied'
        linked.symlink_to(SCRIPTS.parent)
        shutil.copytree(SCRIPTS.parent, copied, ignore=shutil.ignore_patterns('__pycache__'))
        (self.dir / 'alone.py').symlink_to(SCRIPT)
        for script, folder in [(linked / 'scripts/mddt.py', linked), (copied / 'scripts/mddt.py', copied),
                               (self.dir / 'alone.py', SCRIPTS.parent)]:
            out = subprocess.run(['uv', 'run', '--quiet', str(script), str(doc)],
                                 capture_output=True, text=True).stdout
            self.assertIn(f'  rule: {folder / "references/model.md"}#', out, script)

    def test_outline_is_automatic_only_with_structural_findings(self):
        ok = self.write('ok.md', '# T\n\nOverview.\n\n## Part\n\nText.\n')
        self.assertNotIn('outline', run(str(ok)).stdout)
        outline = run('--outline', str(ok)).stdout
        self.assertIn('H1 T  [7 lines; overview]', outline)
        self.assertIn('H2 Part  [3 lines; part]', outline)
        bad = self.write('bad.md', '# T\n')
        self.assertIn('outline', run(str(bad)).stdout)

    def test_directories_include_changelogs_and_hidden_folders(self):
        self.write('CHANGELOG.md', '# Changelog\n\n## 1.0\n\n- one\n')
        (self.dir / '.claude').mkdir()
        self.write('.claude/x.md', '# X\n\nOverview.\n')
        (self.dir / 'node_modules').mkdir()
        self.write('node_modules/y.md', '# Y\n\nOverview.\n')
        self.write('doc.md', '# T\n\nOverview.\n')
        data = json.loads(run('--format', 'json', str(self.dir)).stdout)
        self.assertEqual(sorted(Path(f).name for f in data['files']), ['CHANGELOG.md', 'doc.md', 'x.md'])
        self.assertEqual(data['skipped'], [])

    def test_directories_without_git_are_walked_with_a_notice(self):
        (self.dir / '.git').mkdir()
        self.write('doc.md', '# T\n\nOverview.\n')
        bin_dir = self.dir / 'bin'
        bin_dir.mkdir()
        (bin_dir / 'uv').symlink_to(shutil.which('uv'))
        result = run('--format', 'json', str(self.dir), uv=str(bin_dir / 'uv'),
                     env={**os.environ, 'PATH': str(bin_dir)})
        self.assertEqual([Path(f).name for f in json.loads(result.stdout)['files']], ['doc.md'])
        self.assertIn('.gitignore is not applied', result.stderr)

    def test_github_links_without_git_are_left_alone(self):
        (self.dir / '.git').mkdir()
        self.write('doc.md', '# T\n\nSee [the guide](https://github.com/owner/pkg/blob/main/none.md).\n')
        bin_dir = self.dir / 'bin'
        bin_dir.mkdir()
        (bin_dir / 'uv').symlink_to(shutil.which('uv'))
        result = run('--format', 'json', str(self.dir), uv=str(bin_dir / 'uv'),
                     env={**os.environ, 'PATH': str(bin_dir)})
        self.assertEqual(json.loads(result.stdout)['diagnostics'], [])

    def test_git_repositories_list_the_files_git_sees(self):
        if shutil.which('git') is None:
            self.skipTest('git is not installed')
        subprocess.run(['git', 'init', '--quiet', str(self.dir)], check=True)
        self.write('.gitignore', 'ignored/\n')
        (self.dir / 'ignored').mkdir()
        self.write('ignored/x.md', '# X\n\nOverview.\n')
        self.write('doc.md', '# T\n\nOverview.\n')
        data = json.loads(run('--format', 'json', str(self.dir)).stdout)
        self.assertEqual([Path(f).name for f in data['files']], ['doc.md'])

    def test_self_ignoring_folders_are_skipped_without_git(self):
        self.write('README.md', '# R\n\nOverview.\n')
        (self.dir / '.pytest_cache').mkdir()
        self.write('.pytest_cache/.gitignore', '# Created by pytest automatically.\n*\n')
        self.write('.pytest_cache/README.md', '# pytest cache directory #\n\nCache data.\n')
        (self.dir / '.notes').mkdir()
        self.write('.notes/.gitignore', '*\n!plan.md\n')
        self.write('.notes/plan.md', '# Plan\n\nOverview.\n')
        data = json.loads(run('--format', 'json', str(self.dir)).stdout)
        self.assertEqual(sorted(Path(f).name for f in data['files']), ['README.md', 'plan.md'])

    def test_exclude_matches_paths_from_the_root_however_spelled(self):
        (self.dir / 'sub').mkdir()
        deep = self.write('sub/deep.md', 'no heading\n')
        for arg, cwd in [(str(deep), None), ('sub/deep.md', self.dir), ('deep.md', self.dir / 'sub')]:
            data = json.loads(run('--format', 'json', '--root', str(self.dir), '--exclude', 'sub/*',
                                  arg, cwd=cwd).stdout)
            self.assertEqual(data['files'], [], arg)

    def test_exclude_without_a_tree_root_matches_from_the_current_directory(self):
        if any((folder / '.git').exists() for folder in self.dir.parents):
            self.skipTest('the temporary directory is inside a Git tree')
        (self.dir / 'templates').mkdir()
        self.write('templates/t.md', 'no heading\n')
        data = json.loads(run('--format', 'json', '--exclude', 'templates/*', 'templates/t.md',
                              cwd=self.dir).stdout)
        self.assertEqual(data['files'], [])


class IgnoreFile(CheckerCase):
    """The .mddtignore file: gitignore-style patterns relative to the folder holding it."""
    BAD = 'no heading\n'

    def make(self, files):
        for name, text in files.items():
            path = self.dir / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding='utf-8')

    def selected(self, *args, cwd=None):
        """Return the checked and skipped files, relative to the tree folder, and the findings."""
        data = json.loads(run('--format', 'json', *args, str(self.dir), cwd=cwd).stdout)
        names = lambda found: sorted(Path(f).relative_to(self.dir).as_posix() for f in found)
        return names(data['files']), names(data['skipped']), sorted(
            (Path(d['file']).relative_to(self.dir).as_posix(), d['code']) for d in data['diagnostics'])

    def skipped_by(self, patterns, paths):
        self.make({'.mddtignore': patterns, **{p: '# T\n\nOverview.\n' for p in paths}})
        return self.selected('--root', str(self.dir))[1]

    def test_ignored_files_are_skipped_not_checked(self):
        self.make({'README.md': '# R\n\nSee [A](a.md).\n', 'a.md': '# A\n\nOverview.\n',
                   'raw/x.md': self.BAD, '.mddtignore': 'raw/\n'})
        checked, skipped, found = self.selected()
        self.assertEqual((checked, skipped, found), (['README.md', 'a.md'], ['raw/x.md'], []))

    def test_pattern_syntax(self):
        paths = ['a.md', 'sub/a.md', 'sub/deep/a.md', 'b1.md', 'keep.md', 'gen/x.md', 'docs/g/y.md', 'docs/z.md']
        cases = [
            ('# comment\n\na.md\n', ['a.md', 'sub/a.md', 'sub/deep/a.md']),
            ('/a.md\n', ['a.md']),
            ('sub/a.md\n', ['sub/a.md']),
            ('*.md\n!keep.md\n', [p for p in paths if p != 'keep.md']),
            ('b?.md\n[ab].md\n', ['a.md', 'sub/a.md', 'sub/deep/a.md', 'b1.md']),
            ('gen/\ngen\n', ['gen/x.md']),
            ('gen/**\n', ['gen/x.md']),
            ('**/deep/a.md\n', ['sub/deep/a.md']),
            ('docs/**/y.md\n', ['docs/g/y.md']),
            ('docs/*.md\n', ['docs/z.md']),
            ('sub/*/a.md\n', ['sub/deep/a.md']),
            ('a.md\n!sub/a.md\n', ['a.md', 'sub/deep/a.md']),
            ('gen/\n!gen/x.md\n', ['gen/x.md']),
            ('\\#x.md\n/keep.md   \n', ['keep.md']),
        ]
        for patterns, expected in cases:
            with self.subTest(patterns=patterns):
                self.assertEqual(self.skipped_by(patterns, paths), sorted(expected))

    def test_directory_pattern_does_not_match_a_file_of_that_name(self):
        self.assertEqual(self.skipped_by('a.md/\n', ['a.md']), [])

    def test_escaped_and_bracket_patterns(self):
        self.assertEqual(self.skipped_by('\\#x.md\n[!a]*.md\n', ['#x.md', 'a.md', 'b.md']), ['#x.md', 'b.md'])
        self.assertEqual(self.skipped_by('[a.md\n', ['[a.md', 'a.md']), ['[a.md'])
        self.assertEqual(self.skipped_by('[]x].md\n', [']a.md', '].md', 'x.md']), ['].md', 'x.md'])
        self.assertEqual(self.skipped_by('a**c.md\n/\n', ['abc.md', 'a/c.md']), ['abc.md'])

    def test_folder_files_apply_to_their_folder_and_deeper_ones_win(self):
        self.make({'.mddtignore': 'a.md\n', 'a.md': self.BAD, 'sub/a.md': self.BAD, 'sub/b.md': self.BAD,
                   'sub/.mddtignore': '!a.md\n/b.md\n', 'other/a.md': self.BAD, 'other/b.md': self.BAD,
                   'other/sub/b.md': self.BAD})
        checked, skipped, _ = self.selected('--root', str(self.dir))
        self.assertEqual(skipped, ['a.md', 'other/a.md', 'sub/b.md'])
        self.assertEqual(checked, ['other/b.md', 'other/sub/b.md', 'sub/a.md'])

    def test_a_file_in_an_ignored_folder_cannot_be_reincluded_by_a_deeper_file(self):
        self.make({'.mddtignore': 'raw/\n', 'raw/x.md': self.BAD, 'raw/.mddtignore': '!x.md\n'})
        self.assertEqual(self.selected('--root', str(self.dir))[:2], ([], ['raw/x.md']))

    def test_file_is_read_even_when_git_ignores_it(self):
        if shutil.which('git') is None:
            self.skipTest('git is not installed')
        subprocess.run(['git', 'init', '--quiet', str(self.dir)], check=True)
        self.make({'.gitignore': '.mddtignore\nignored/\n', '.mddtignore': 'raw.md\n', 'raw.md': self.BAD,
                   'ignored/x.md': self.BAD, 'doc.md': '# D\n\nOverview.\n'})
        subprocess.run(['git', '-C', str(self.dir), 'check-ignore', '-q', '.mddtignore'], check=True)
        checked, skipped, found = self.selected()
        self.assertEqual((checked, skipped, found), (['doc.md'], ['raw.md'], []))

    def test_union_with_exclude(self):
        self.make({'.mddtignore': 'one.md\n', 'one.md': self.BAD, 'two.md': self.BAD, 'three.md': self.BAD})
        checked, skipped, _ = self.selected('--root', str(self.dir), '--exclude', 'two.md')
        self.assertEqual((checked, skipped), (['three.md'], ['one.md', 'two.md']))

    def test_explicit_file_arguments_are_skipped_however_spelled(self):
        self.make({'.mddtignore': 'sub/\n', 'sub/x.md': self.BAD})
        for arg, cwd in [(str(self.dir / 'sub/x.md'), None), ('sub/x.md', self.dir), ('x.md', self.dir / 'sub')]:
            data = json.loads(run('--format', 'json', '--root', str(self.dir), arg, cwd=cwd).stdout)
            self.assertEqual((data['files'], len(data['skipped'])), ([], 1), arg)

    def test_the_tree_root_bounds_which_files_are_read(self):
        self.make({'.mddtignore': 'x.md\n', 'sub/x.md': self.BAD, 'sub/y.md': self.BAD})
        sub = self.dir / 'sub'
        data = json.loads(run('--format', 'json', '--root', str(sub), str(sub)).stdout)
        self.assertEqual(len(data['files']), 2)

    def test_a_file_outside_the_root_uses_its_own_folder(self):
        root = self.dir / 'tree'
        self.make({'tree/.mddtignore': 'x.md\n', 'out/.mddtignore': 'x.md\n', 'out/x.md': self.BAD,
                   'out/y.md': self.BAD})
        data = json.loads(run('--format', 'json', '--root', str(root), str(self.dir / 'out/x.md'),
                              str(self.dir / 'out/y.md')).stdout)
        self.assertEqual([Path(f).name for f in data['files']], ['y.md'])

    def test_without_a_tree_root_patterns_are_relative_to_the_current_directory(self):
        if any((folder / '.git').exists() for folder in self.dir.parents):
            self.skipTest('the temporary directory is inside a Git tree')
        self.make({'.mddtignore': 'templates/\n', 'templates/t.md': self.BAD})
        data = json.loads(run('--format', 'json', 'templates/t.md', cwd=self.dir).stdout)
        self.assertEqual(data['files'], [])

    def test_ignored_files_still_resolve_links_and_parents(self):
        self.make({'.mddtignore': 'raw/\nspec.md\n',
                   'README.md': '# R\n\nSee [A](a.md) and [raw](raw/index.md).\n',
                   'a.md': '# A\n\nSee [spec](spec.md#goal) and [raw](raw/index.md#top).\n',
                   'spec.md': '# Spec\n\nOverview.\n\n## Goal\n\nText.\n',
                   'raw/index.md': '# Top\n\nSee [child](child.md).\n',
                   'raw/child.md': self.BAD, 'raw/more/extra.md': self.BAD})
        checked, skipped, found = self.selected('--root', str(self.dir))
        self.assertEqual((checked, skipped, found), (['README.md', 'a.md'],
                         ['raw/child.md', 'raw/index.md', 'raw/more/extra.md', 'spec.md'], []))
        self.make({'a.md': '# A\n\nSee [spec](spec.md#nowhere) and [gone](gone.md).\n'})
        self.assertEqual(self.selected('--root', str(self.dir))[2],
                         [('a.md', 'anchor-missing'), ('a.md', 'link-broken')])

    def test_an_ignored_parent_still_decides_whether_a_child_is_linked(self):
        self.make({'.mddtignore': 'docs/index.md\n', 'README.md': '# R\n\nSee [docs](docs/).\n',
                   'docs/index.md': '# Docs\n\nSee [A](a.md).\n', 'docs/a.md': '# A\n\nOverview.\n',
                   'docs/b.md': '# B\n\nOverview.\n'})
        self.assertEqual(self.selected('--root', str(self.dir))[2], [('docs/b.md', 'doc-unlinked')])

    def test_unreadable_file_is_a_usage_error(self):
        self.make({'doc.md': '# T\n\nOverview.\n'})
        (self.dir / '.mddtignore').write_bytes('caf\u00e9.md\n'.encode('latin-1'))
        result = run(str(self.dir / 'doc.md'))
        self.assertEqual(result.returncode, 2)
        self.assertIn('.mddtignore', result.stderr)

    def test_text_output_reports_ignored_files_as_skipped(self):
        self.make({'.mddtignore': 'raw.md\n', 'raw.md': self.BAD, 'doc.md': '# D\n\nOverview.\n'})
        out = run('--root', str(self.dir), str(self.dir)).stdout
        self.assertIn('skipped: ', out)
        self.assertIn('raw.md', out)


SKILL = ROOT / 'skills/mddt'
CODE_COMMENT = re.compile(r'<!-- code: ([^>]*?) -->')
LINK = re.compile(r'\]\(([^)\s]+)\)')


def slug(heading):
    """GitHub-style anchor for a heading."""
    text = re.sub(r'[^\w\- ]', '', heading.strip().lower())
    return text.replace(' ', '-')


def anchors(path):
    in_fence = False
    found = set()
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.startswith('```'):
            in_fence = not in_fence
        elif not in_fence and re.match(r'#{1,6} ', line):
            found.add(slug(line.lstrip('#')))
    return found


def skill_docs():
    return [SKILL / 'SKILL.md', *sorted((SKILL / 'references').glob('*.md'))]


def rule_markers():
    """Return (code, document name, enclosing heading anchors) for each code marker.

    Markers inside fenced code are examples, not rule markers, so they are left out.
    """
    found = []
    for doc in skill_docs():
        stack, in_fence = [], False
        for line in doc.read_text(encoding='utf-8').splitlines():
            if line.startswith('```'):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if m := re.match(r'(#{1,6}) ', line):
                level = len(m.group(1))
                stack = [s for s in stack if s[0] < level] + [(level, slug(line.lstrip('#')))]
            for group in CODE_COMMENT.findall(line):
                found.extend((code.strip(), doc.name, {s[1] for s in stack}) for code in group.split(','))
    return found


def checker_constant(name):
    """Evaluate a literal assigned at the top level of the checker."""
    source = (SCRIPTS / 'mddt.py').read_text(encoding='utf-8')
    return ast.literal_eval(re.search(rf'^{name} = (.+)$', source, re.M).group(1))


class Registry(unittest.TestCase):
    def test_registry_entries_hold_valid_metadata(self):
        with (SCRIPTS / 'rules.toml').open('rb') as f:
            registry = tomllib.load(f)
        severities, groups = set(checker_constant('SEVERITY_ORDER')), set(checker_constant('GROUP_ORDER'))
        for code, entry in registry.items():
            with self.subTest(code=code):
                self.assertEqual(set(entry), {'severity', 'group', 'summary', 'rule'})
                self.assertIn(entry['severity'], severities)
                self.assertIn(entry['group'], groups)
                for key in ('summary', 'rule'):
                    self.assertIsInstance(entry[key], str)
                    self.assertTrue(entry[key].strip())

    def test_rule_documents_mark_every_registered_code_once(self):
        with (SCRIPTS / 'rules.toml').open('rb') as f:
            codes = sorted(tomllib.load(f))
        self.assertEqual(sorted(code for code, _, _ in rule_markers()), codes)

    def test_registry_rule_locations_hold_their_markers(self):
        with (SCRIPTS / 'rules.toml').open('rb') as f:
            registry = tomllib.load(f)
        enclosing = {code: (name, anchors) for code, name, anchors in rule_markers()}
        for code, entry in registry.items():
            name, _, anchor = entry['rule'].partition('#')
            self.assertEqual(enclosing[code][0], name, code)
            self.assertIn(anchor, enclosing[code][1], code)

    def test_stated_limits_match_the_checker(self):
        source = (SCRIPTS / 'mddt.py').read_text(encoding='utf-8')
        limit = {name: int(value) for name, value in re.findall(r'^(MAX_\w+) = (\d+)$', source, re.M)}
        model = (SKILL / 'references' / 'model.md').read_text(encoding='utf-8')
        with (SCRIPTS / 'rules.toml').open('rb') as f:
            summary = {code: entry['summary'] for code, entry in tomllib.load(f).items()}
        word = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
        ordinal = ['zeroth', 'first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh']
        sentences, run_after = word[limit['MAX_SENTENCES']], word[limit['MAX_PARAGRAPH_RUN'] + 1]
        items, words = word[limit['MAX_LIST_ITEMS']], limit['MAX_WORDS']
        heading, depth = limit['MAX_HEADING_LEVEL'], limit['MAX_LIST_DEPTH']
        for text, phrase in [
            (model, f'at most {sentences} sentence units'),
            (summary['paragraph-length'], f'more than {sentences} sentence units'),
            (model, f'{run_after.capitalize()} or more paragraphs in a row'),
            (summary['paragraph-run'], f'{run_after} or more paragraphs'),
            (model, f'at most {words} words'),
            (summary['sentence-length'], f'more than {words} words'),
            (model, f'about {items} items'),
            (summary['list-length'], f'more than {items} items'),
            (summary['section-count'], f'more than {items} sibling sections'),
            (model, f'about {items} unless in mechanical order'),
            (model, f'headings stop at H{heading}.'),
            (summary['heading-depth'], f'deeper than H{heading}'),
            (model, f'Lists nest at most {word[depth]} levels'),
            (model, f'A {ordinal[depth + 1]} level is not allowed, and a {ordinal[depth]} level is allowed'),
            (summary['list-depth-4'], f'nested {word[depth + 1]} or more levels deep'),
            (summary['list-depth-3'], f'nested {word[depth]} levels deep'),
        ]:
            self.assertIn(phrase, text)

    def test_checker_reference_lists_every_option(self):
        source = (SCRIPTS / 'mddt.py').read_text(encoding='utf-8')
        options = re.findall(r"add_argument\('(--[a-z-]+)'", source)
        self.assertGreater(len(options), 3)
        reference = (SKILL / 'references' / 'checker.md').read_text(encoding='utf-8')
        for option in options:
            self.assertIn(f'`{option}', reference)

    def test_checker_reference_names_every_json_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc = Path(tmp, 'doc.md')
            doc.write_text('# T\n', encoding='utf-8')
            data = json.loads(run('--format', 'json', '--outline', str(doc)).stdout)
        reference = (SKILL / 'references' / 'checker.md').read_text(encoding='utf-8')
        for key in [*data, *data['diagnostics'][0]]:
            self.assertIn(f'`{key}`', reference)

    def test_example_results_follow_the_model(self):
        # The "After" side of each example must itself conform; snippets are
        # fragments, so codes about whole files, parents, and the files that
        # their links name do not apply.
        text = (SKILL / 'references' / 'examples.md').read_text(encoding='utf-8')
        snippets = re.findall(r'(?:After:|In `[^`]+`:)\n\n```markdown\n(.*?)```', text, re.S)
        self.assertGreater(len(snippets), 5)
        with tempfile.TemporaryDirectory() as tmp:
            for n, snippet in enumerate(snippets):
                Path(tmp, f'after{n}.md').write_text(snippet, encoding='utf-8')
            data = json.loads(run('--format', 'json', '--review', tmp).stdout)
        whole_file = {'h1-missing', 'h1-overview', 'doc-unlinked', 'link-broken', 'anchor-missing'}
        self.assertEqual([d for d in data['diagnostics'] if d['code'] not in whole_file], [])

    def test_links_between_skill_documents_resolve(self):
        for doc in skill_docs():
            text = re.sub(r'(?ms)^```.*?^```', '', doc.read_text(encoding='utf-8'))
            for target in LINK.findall(text):
                if '://' in target:
                    continue
                name, _, anchor = target.partition('#')
                linked = (doc.parent / name).resolve() if name else doc
                self.assertTrue(linked.is_file(), f'{doc.name}: {target}')
                if anchor:
                    self.assertIn(anchor, anchors(linked), f'{doc.name}: {target}')

    def test_every_code_has_fix_guidance_and_vice_versa(self):
        with (SCRIPTS / 'rules.toml').open('rb') as f:
            codes = list(tomllib.load(f))
        with (SCRIPTS / 'fixes.toml').open('rb') as f:
            fixes = tomllib.load(f)
        self.assertEqual(codes, list(fixes))
        self.assertTrue(all(isinstance(text, str) and text.strip() for text in fixes.values()))


if __name__ == '__main__':
    unittest.main()
