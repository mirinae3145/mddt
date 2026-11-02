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

    def test_name_forms_are_compared_per_topic(self):
        text = ('# T\n\nOverview.\n\n## Topic A\n\nOverview.\n\n### One\n\nList:\n\n- **a**: x\n- **b**: y\n\n'
                '### Two\n\nList:\n\n- c: x\n- d: y\n\n'
                '## Topic B\n\nOverview.\n\n### Three\n\nList:\n\n- e: x\n- f: y\n\n### Four\n\nText.\n')
        self.assertEqual(self.codes(text), [('name-form-mix', 20)])

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

    def test_exclude_skips_non_documents(self):
        found = self.tree({
            'README.md': '# R\n\nOverview.\n',
            'templates/case.md': 'no heading\n',
        })
        self.assertEqual(found, [('templates/case.md', 'doc-unlinked'), ('templates/case.md', 'h1-missing')])
        data = json.loads(run('--format', 'json', '--exclude', 'templates/*', str(self.dir)).stdout)
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

    def test_sibling_imbalance_and_file_size(self):
        big = ''.join(f'Line {n}.\n\n' for n in range(30))
        text = f'# T\n\nOverview.\n\n## A\n\nShort.\n\n## B\n\n{big}## C\n\nShort.\n'
        found = self.tree({'README.md': text}, '--review')
        self.assertIn(('README.md', 'sibling-imbalance'), found)
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

    def test_directories_skip_changelogs_and_hidden_folders(self):
        self.write('CHANGELOG.md', '## 1.0\n\n- one\n')
        (self.dir / '.hidden').mkdir()
        self.write('.hidden/x.md', '## no h1\n')
        self.write('doc.md', '# T\n\nOverview.\n')
        data = json.loads(run('--format', 'json', str(self.dir)).stdout)
        self.assertEqual([Path(f).name for f in data['files']], ['doc.md'])
        self.assertEqual([Path(f).name for f in data['skipped']], ['CHANGELOG.md'])


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

    def test_registry_rule_locations_exist(self):
        with (SCRIPTS / 'rules.toml').open('rb') as f:
            registry = tomllib.load(f)
        for code, entry in registry.items():
            name, _, anchor = entry['rule'].partition('#')
            doc = SKILL / 'references' / name
            self.assertTrue(doc.is_file(), code)
            self.assertIn(anchor, anchors(doc), code)

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
