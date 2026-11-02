# SPDX-FileCopyrightText: 2026 Taeha Shin
# SPDX-License-Identifier: MIT
"""Behavioral checks through the checker's command-line interface."""
import json
from pathlib import Path
import re
import subprocess
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/mddt/scripts'
SCRIPT = SCRIPTS / 'mddt.py'


def run(*args, cwd=None):
    return subprocess.run(['uv', 'run', '--quiet', str(SCRIPT), *args],
                          capture_output=True, text=True, cwd=cwd)


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
        self.assertCodes('# T\n\n[![b](x.svg)](y)\n\n<!-- note -->\n\nOverview.\n', [])
        self.assertCodes('# T\n\n[![b](x.svg)](y)\n\n## Part\n\nText.\n', ['h1-overview'])
        self.assertCodes('# T\n\n```\ncode\n```\n', ['h1-overview'])

    def test_heading_skip_and_depth(self):
        self.assertCodes('# T\n\nOverview.\n\n### Deep\n\nText.\n', ['heading-skip'])
        self.assertCodes(
            '# T\n\nOverview.\n\n## Topic\n\nOverview.\n\n### A\n\nX.\n\n#### B\n\nY.\n\n### C\n\nZ.\n',
            ['heading-depth'])

    def test_section_numbers_in_sequence(self):
        self.assertCodes('# T\n\nOverview.\n\n## 1. Start\n\nA.\n\n## 2. Next\n\nB.\n', ['heading-number'])
        self.assertCodes('# T\n\nOverview.\n\n## A. Start\n\nA.\n\n## B. Next\n\nB.\n', ['heading-number'])
        self.assertCodes('# T\n\nOverview.\n\n## 2.0 migration\n\nA.\n\n## 3.0 migration\n\nB.\n', [])
        self.assertCodes('# T\n\nOverview.\n\n## 2026-10-30 review\n\nA.\n\n## 2026-10-31 review\n\nB.\n', [])
        self.assertCodes('# T\n\nOverview.\n\n## 3 things to know\n\nA.\n\n## Other\n\nB.\n', [])

    def test_subject_numbers_in_headings_stay(self):
        for first, second in [('2025 review', '2026 review'), ('1.4 (2026-01-10)', '1.5 (2026-02-01)'),
                              ('1.4 release notes', '1.5 release notes'), ('2 players', '3 players')]:
            self.assertCodes(f'# T\n\nOverview.\n\n## {first}\n\nA.\n\n## {second}\n\nB.\n', [])

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

    def test_topic_single_child(self):
        self.assertCodes(
            '# T\n\nOverview.\n\n## Topic\n\nOverview.\n\n### Only\n\nX.\n', ['topic-single-child'])

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
        self.assertCodes('# T\n\nOverview.\n\n## Items\n\n- x\n- y\n\nAfter.\n', ['list-intro'])

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

    def test_named_item_with_named_descendant(self):
        self.assertCodes(
            '# T\n\nOverview.\n\nList:\n\n- **Outer**: text\n  - **Inner**: text\n  - plain\n- **Other**: x\n',
            ['name-nesting'])
        self.assertCodes(
            '# T\n\nOverview.\n\nList:\n\n- **Outer**: text\n  - Inner: text\n  - plain\n- **Other**: x\n',
            ['name-nesting', 'name-form-mix'])

    def test_items_of_several_sentences_are_blocks(self):
        long = 'First sentence.\n  Second sentence.'
        self.assertEqual(self.review(f'# T\n\nOverview.\n\nList:\n\n- {long}\n- short\n'), ['item-name'])
        self.assertEqual(self.review(f'# T\n\nOverview.\n\nSteps:\n\n1. {long}\n1. short\n'), [])
        self.assertEqual(self.review(f'# T\n\nOverview.\n\nList:\n\n- **Name**: {long}\n- **Other**: x\n'), [])
        nested = f'# T\n\nOverview.\n\nList:\n\n- **Name**: rule.\n  - {long}\n  - short\n- **Other**: x\n'
        self.assertEqual(self.review(nested), ['nested-block'])

    def test_name_forms_are_compared_per_topic(self):
        text = ('# T\n\nOverview.\n\n## Topic A\n\nOverview.\n\n### One\n\nList:\n\n- **a**: x\n- **b**: y\n\n'
                '### Two\n\nList:\n\n- c: x\n- d: y\n\n'
                '## Topic B\n\nOverview.\n\n### Three\n\nList:\n\n- e: x\n- f: y\n\n### Four\n\nText.\n')
        self.assertEqual(self.codes(text), [('name-form-mix', 20)])

    def test_step_ending_in_colon_is_not_a_name(self):
        self.assertCodes(
            '# T\n\nOverview.\n\nList:\n\n- **A**: x\n- Install the tool with pipx:\n\n  ```sh\n  pipx install t\n  ```\n- **B**: y\n', [])

    def test_link_names_do_not_count_as_a_form(self):
        self.assertCodes(
            '# T\n\nOverview.\n\n## Docs\n\n- [A](a.md): what A covers.\n- [B](b.md): what B covers.\n\n'
            '## Scope\n\n- **In**: x\n- **Out**: y\n', [])

    def test_prose_starting_with_link_or_time_is_not_a_name(self):
        self.assertCodes(
            '# T\n\nOverview.\n\nList:\n\n- **A**: x\n'
            '  - [Spec](u)을 확인했다.\n  - Meet at 10:30 today.\n- **B**: y\n', [])


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
        self.assertCodes('# T\n\nSee `a.b` and [Spec. One](u) now.\n', [])
        self.assertCodes('# T\n\n보관함을 스캔한다. `tool scan PATH`\n', [])


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
            'README.md': '# R\n\nSee [part](other.md#part), [topic](other.md#topic), [file](other.md).\n',
            'other.md': '# O\n\nOverview.\n\n## Part\n\nText.\n\n## Topic\n\nOverview.\n\n### A\n\nX.\n\n### B\n\nY.\n',
        }
        self.assertEqual(self.tree(files), [])
        self.assertEqual(self.tree(files, '--review'), [('README.md', 'anchor-to-part')])

    def test_link_without_summary(self):
        found = self.tree({
            'README.md': '# R\n\nChildren:\n\n- [A](a.md)\n- [B](b.md): what B covers.\n',
            'a.md': '# A\n\nOverview.\n',
            'b.md': '# B\n\nSee [A](a.md).\n',
        }, '--review')
        self.assertEqual(found, [('README.md', 'link-without-summary')])

    def test_section_count_unless_mechanically_ordered(self):
        sections = ''.join(f'## {w}\n\nText.\n\n' for w in 'pear apple fig kiwi plum lime date cherry'.split())
        self.assertEqual(self.tree({'README.md': f'# T\n\nOverview.\n\n{sections}'}), [('README.md', 'section-count')])
        dated = ''.join(f'## 2026-10-{d:02d}\n\nText.\n\n' for d in range(20, 10, -1))
        self.assertEqual(self.tree({'README.md': f'# T\n\nOverview.\n\n{dated}'}), [])

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


class Interface(CheckerCase):
    def test_exit_codes(self):
        ok = self.write('ok.md', '# T\n\nOverview.\n')
        warn = self.write('warn.md', '# T\n\nOverview.\n\nList:\n\n- a\n  - b\n    - c\n    - d\n  - e\n- f\n')
        bad = self.write('bad.md', '# T\n')
        self.assertEqual(run(str(ok)).returncode, 0)
        self.assertEqual(run(str(warn)).returncode, 0)
        self.assertEqual(run(str(bad)).returncode, 1)
        self.assertEqual(run(str(self.dir / 'missing.md')).returncode, 2)

    def test_text_output_groups_locations_and_prints_fix_once(self):
        a = self.write('a.md', '# A\n')
        b = self.write('b.md', '# B\n')
        out = run(str(a), str(b)).stdout
        self.assertEqual(out.count('error h1-overview:'), 1)
        self.assertEqual(out.count('  fix:'), 1)
        self.assertIn(f'{a}:1', out)
        self.assertIn(f'{b}:1', out)

    def test_outline_is_automatic_only_with_structural_findings(self):
        ok = self.write('ok.md', '# T\n\nOverview.\n\n## Part\n\nText.\n')
        self.assertNotIn('outline', run(str(ok)).stdout)
        outline = run('--outline', str(ok)).stdout
        self.assertIn('H1 T  [7 lines; overview]', outline)
        self.assertIn('H2 Part  [3 lines; part]', outline)
        bad = self.write('bad.md', '# T\n')
        self.assertIn('outline', run(str(bad)).stdout)

    def test_directories_skip_changelogs_but_not_hidden_folders(self):
        self.write('CHANGELOG.md', '## 1.0\n\n- one\n')
        (self.dir / '.claude').mkdir()
        self.write('.claude/x.md', '# X\n\nOverview.\n')
        (self.dir / 'node_modules').mkdir()
        self.write('node_modules/y.md', '# Y\n\nOverview.\n')
        self.write('doc.md', '# T\n\nOverview.\n')
        data = json.loads(run('--format', 'json', str(self.dir)).stdout)
        self.assertEqual(sorted(Path(f).name for f in data['files']), ['doc.md', 'x.md'])
        self.assertEqual([Path(f).name for f in data['skipped']], ['CHANGELOG.md'])

    def test_exclude_matches_paths_from_the_root_however_spelled(self):
        (self.dir / 'sub').mkdir()
        deep = self.write('sub/deep.md', 'no heading\n')
        for arg, cwd in [(str(deep), None), ('sub/deep.md', self.dir), ('deep.md', self.dir / 'sub')]:
            data = json.loads(run('--format', 'json', '--root', str(self.dir), '--exclude', 'sub/*',
                                  arg, cwd=cwd).stdout)
            self.assertEqual(data['files'], [], arg)


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


class Registry(unittest.TestCase):
    def test_rule_documents_mark_every_registered_code(self):
        with (SCRIPTS / 'rules.toml').open('rb') as f:
            codes = set(tomllib.load(f))
        marked = set()
        for doc in skill_docs():
            for group in CODE_COMMENT.findall(doc.read_text(encoding='utf-8')):
                marked.update(code.strip() for code in group.split(','))
        self.assertEqual(codes, marked)

    def test_registry_rule_locations_hold_their_markers(self):
        with (SCRIPTS / 'rules.toml').open('rb') as f:
            registry = tomllib.load(f)
        enclosing = {}
        for doc in skill_docs():
            stack, in_fence = [], False
            for line in doc.read_text(encoding='utf-8').splitlines():
                if line.startswith('```'):
                    in_fence = not in_fence
                elif not in_fence and (m := re.match(r'(#{1,6}) ', line)):
                    level = len(m.group(1))
                    stack = [s for s in stack if s[0] < level] + [(level, slug(line.lstrip('#')))]
                for group in CODE_COMMENT.findall(line):
                    for code in group.split(','):
                        enclosing[code.strip()] = (doc.name, {s[1] for s in stack})
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
        sentences, run_after = word[limit['MAX_SENTENCES']], word[limit['MAX_PARAGRAPH_RUN'] + 1]
        items, words = word[limit['MAX_LIST_ITEMS']], limit['MAX_WORDS']
        for text, phrase in [
            (model, f'at most {sentences} sentences'),
            (summary['paragraph-length'], f'more than {sentences} sentences'),
            (model, f'{run_after.capitalize()} or more paragraphs in a row'),
            (summary['paragraph-run'], f'{run_after} or more paragraphs'),
            (model, f'at most {words} words'),
            (summary['sentence-length'], f'more than {words} words'),
            (model, f'about {items} items'),
            (summary['list-length'], f'more than {items} items'),
            (summary['section-count'], f'more than {items} sibling sections'),
        ]:
            self.assertIn(phrase, text)

    def test_example_results_follow_the_model(self):
        # The "After" side of each example must itself conform; snippets are
        # fragments, so codes about whole files and parents do not apply.
        text = (SKILL / 'references' / 'examples.md').read_text(encoding='utf-8')
        snippets = re.findall(r'(?:After:|In `[^`]+`:)\n\n```markdown\n(.*?)```', text, re.S)
        self.assertGreater(len(snippets), 5)
        with tempfile.TemporaryDirectory() as tmp:
            for n, snippet in enumerate(snippets):
                Path(tmp, f'after{n}.md').write_text(snippet, encoding='utf-8')
            data = json.loads(run('--format', 'json', '--review', tmp).stdout)
        whole_file = {'h1-missing', 'h1-overview', 'doc-unlinked'}
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
