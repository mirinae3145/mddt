# SPDX-FileCopyrightText: 2026 Taeha Shin
# SPDX-License-Identifier: MIT
"""Behavioral checks of the mddt hook through its event interface."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / 'skills/mddt/scripts/mddt_hook.py'
SKILL = ROOT / 'skills/mddt/SKILL.md'


def run(payload):
    """Run the hook as an agent host would, with one event on stdin."""
    text = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run([sys.executable, str(HOOK)], input=text, capture_output=True, text=True)


class HookCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, lines=10):
        path = self.dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(''.join(f'line {i}\n' for i in range(lines)), encoding='utf-8')
        return path

    def event(self, tool, tool_input):
        return {'hook_event_name': 'PreToolUse', 'cwd': str(self.dir),
                'tool_name': tool, 'tool_input': tool_input}

    def respond(self, payload):
        result = run(payload)
        self.assertEqual(result.returncode, 0, result.stderr)
        if not result.stdout:
            return None
        output = json.loads(result.stdout)['hookSpecificOutput']
        self.assertEqual(output['hookEventName'], 'PreToolUse')
        return output

    def decide(self, payload):
        """Return the reason of a denial, or None when the call proceeds without one."""
        output = self.respond(payload)
        if output is None or 'permissionDecision' not in output:
            return None
        self.assertEqual(output['permissionDecision'], 'deny')
        self.assertIn(str(SKILL), output['permissionDecisionReason'])
        return output['permissionDecisionReason']

    def context(self, tool, tool_input):
        """Return the context added to a call, checking that the call proceeds."""
        output = self.respond(self.event(tool, tool_input))
        if output is None:
            return None
        self.assertNotIn('permissionDecision', output)
        self.assertIn(str(SKILL), output['additionalContext'])
        return output['additionalContext']

    def read(self, path, **options):
        return self.decide(self.event('Read', {'file_path': str(path), **options}))

    def shell(self, command):
        return self.decide(self.event('Bash', {'command': command}))


class ReadTool(HookCase):
    def test_partial_reads_of_covered_files_are_denied(self):
        for name in ('README.md', 'docs/readme.md', 'CONTRIBUTING.md', 'SKILL.md',
                     'AGENTS.md', 'CLAUDE.md', 'GEMINI.md'):
            path = self.write(name)
            with self.subTest(name=name):
                reason = self.read(path, limit=5)
                self.assertIn(Path(name).name, reason)
                self.assertIn('without offset or limit', reason)
                self.assertIsNotNone(self.read(path, offset=6))

    def test_whole_reads_pass(self):
        path = self.write('README.md')
        self.assertIsNone(self.read(path))
        self.assertIsNone(self.read(path, offset=None, limit=None))

    def test_range_covering_the_whole_file_passes(self):
        path = self.write('README.md', lines=10)
        self.assertIsNone(self.read(path, offset=1, limit=10))
        self.assertIsNone(self.read(path, limit=2000))
        self.assertIsNotNone(self.read(path, offset=2, limit=2000))

    def test_files_too_large_to_read_at_once_pass(self):
        path = self.write('README.md', lines=2001)
        self.assertIsNone(self.read(path, limit=100))
        big = self.dir / 'big/README.md'
        big.parent.mkdir()
        big.write_text('x' * (256 * 1024 + 1), encoding='utf-8')
        self.assertIsNone(self.read(big, limit=1))

    def test_missing_files_pass(self):
        self.assertIsNone(self.read(self.dir / 'README.md', limit=5))

    def test_relative_paths_resolve_from_the_event_directory(self):
        self.write('README.md')
        self.assertIsNotNone(self.read('README.md', limit=5))

    def test_documents_an_ignore_file_leaves_out_are_still_read_whole(self):
        (self.dir / '.mddtignore').write_text('*\n', encoding='utf-8')
        self.assertIsNotNone(self.read(self.write('README.md'), limit=5))

    def test_other_files_pass(self):
        for name in ('notes.md', 'README.txt', 'README.md.bak', 'myREADME.md'):
            with self.subTest(name=name):
                self.assertIsNone(self.read(self.write(name), limit=5))


class ShellCommands(HookCase):
    def test_truncated_reads_are_denied(self):
        commands = {
            'head -80 README.md': 'README.md',
            'cat README.md | head -80': 'README.md',
            'ls -la && cat README.md | head -80': 'README.md',
            'cat README.md 2>&1 | head -80': 'README.md',
            'tail -n +80 docs/README.md': 'README.md',
            'sed -n 80,200p CONTRIBUTING.md': 'CONTRIBUTING.md',
            'sed 80q SKILL.md': 'SKILL.md',
            "awk 'NR<10' AGENTS.md": 'AGENTS.md',
            'head -5 < CLAUDE.md': 'CLAUDE.md',
            'nl GEMINI.md | sed -n 1,20p': 'GEMINI.md',
            'FOO=1 /usr/bin/head -3 readme.md': 'readme.md',
            'cd /x && ls\ncat README.md | head -3': 'README.md',
            '# preview the guide\nhead -40 README.md': 'README.md',
            'echo a#b; head -5 README.md': 'README.md',
            'head -5 \\\n  README.md': 'README.md',
            'sed --quiet 1,5p README.md': 'README.md',
            'sed -e 1,5p -e 5q README.md': 'README.md',
            "bash -lc 'head -5 README.md'": 'README.md',
        }
        for command, name in commands.items():
            with self.subTest(command=command):
                reason = self.shell(command)
                self.assertIsNotNone(reason)
                self.assertIn(name, reason)
                self.assertIn('print it whole with cat', reason)

    def test_whole_reads_searches_and_edits_pass(self):
        for command in ('cat README.md', 'grep -n Install README.md | head',
                        'wc -l README.md', "sed -i 's/a/b/' README.md",
                        'git log --oneline -- README.md | head -5', 'git show HEAD:README.md | head',
                        'head -3 notes.md', 'cat notes.md | head', 'cat "README.md | head"',
                        "awk '{print $1}' README.md", 'echo README.md; head -3 notes.md',
                        "sed -i 's/1 quarter/2 quarters/' README.md", "sed 's/1 quarter/2 quarters/' README.md",
                        'tail -n +3 draft.md > README.md', "sed -n '1,10p' template.md >> docs/README.md",
                        'head -5 notes.md 2> README.md', 'awk \'{print NR": "$0}\' README.md',
                        'cat README.md | grep -n install | head', 'grep -n install < README.md | head',
                        "bash -lc 'cat README.md'", '# head -5 README.md'):
            with self.subTest(command=command):
                self.assertIsNone(self.shell(command))

    def test_files_too_large_to_read_at_once_pass(self):
        self.write('README.md', lines=2001)
        self.assertIsNone(self.shell('head -80 README.md'))
        self.write('CONTRIBUTING.md')
        self.assertIsNotNone(self.shell('head -5 CONTRIBUTING.md'))

    def test_unbalanced_quotes_fall_back_to_words(self):
        self.assertIsNotNone(self.shell("head -80 README.md; echo 'unclosed"))

    def test_command_given_as_a_list(self):
        self.assertIsNotNone(self.decide(self.event('Bash', {'command': ['head', '-5', 'README.md']})))
        self.assertIsNotNone(self.decide(self.event('Bash', {'command': ['bash', '-lc', 'head -5 README.md']})))
        self.assertIsNone(self.decide(self.event('Bash', {'command': ['bash', '-lc', 'cat README.md']})))


class HeadingEdits(HookCase):
    def test_edit_adding_a_heading_names_the_skill_and_procedure(self):
        text = self.context('Edit', {'file_path': str(self.dir / 'notes.md'),
                                     'old_string': 'Some notes.', 'new_string': 'Some notes.\n\n## Usage\n\nRun it.'})
        self.assertIn('notes.md', text)
        self.assertIn('references/writing.md', text)
        self.assertIn('Load it if it is not loaded', text)

    def test_edits_without_new_headings_pass(self):
        path = str(self.dir / 'notes.md')
        for old, new in (('Some notes.', 'Other notes.'), ('## Old', '## New'),
                         ('Text.', 'Text.\n\n```\n# a comment in code\n```'),
                         ('Text.', 'Text with #hashtag.'), ('## A\n\n## B', '## A')):
            with self.subTest(new=new):
                self.assertIsNone(self.context('Edit', {'file_path': path, 'old_string': old, 'new_string': new}))

    def test_other_files_pass(self):
        self.assertIsNone(self.context('Edit', {'file_path': str(self.dir / 'run.py'),
                                                'old_string': 'x', 'new_string': '# comment\nx'}))

    def test_documents_an_ignore_file_leaves_out_pass(self):
        (self.dir / '.mddtignore').write_text('# Kept as received.\noriginals/\n', encoding='utf-8')
        (self.dir / 'notes').mkdir()
        (self.dir / 'notes/.mddtignore').write_text('*.md\n!kept.md\n', encoding='utf-8')
        edit = {'old_string': 'Text.', 'new_string': 'Text.\n\n## Part\n'}
        for name in ('originals/source.md', 'originals/deeper/source.md', 'notes/draft.md'):
            with self.subTest(name=name):
                self.assertIsNone(self.context('Edit', {'file_path': str(self.dir / name), **edit}))
        for name in ('guide.md', 'notes/kept.md', 'originals.md'):
            with self.subTest(name=name):
                self.assertIsNotNone(self.context('Edit', {'file_path': str(self.dir / name), **edit}))
        patch = ('*** Begin Patch\n*** Update File: originals/source.md\n@@\n+## Part\n'
                 '*** Update File: guide.md\n@@\n+## Part\n*** End Patch\n')
        text = self.context('apply_patch', {'command': patch})
        self.assertIn('guide.md', text)
        self.assertNotIn('source.md', text)

    def test_ignore_files_above_the_git_root_are_not_read(self):
        (self.dir / '.mddtignore').write_text('*.md\n', encoding='utf-8')
        (self.dir / 'repo/.git').mkdir(parents=True)
        edit = {'old_string': 'Text.', 'new_string': 'Text.\n\n## Part\n'}
        self.assertIsNotNone(self.context('Edit', {'file_path': str(self.dir / 'repo/doc.md'), **edit}))
        # Without a Git root, every folder above the document is read.
        self.assertIsNone(self.context('Edit', {'file_path': str(self.dir / 'other/doc.md'), **edit}))

    def test_unreadable_ignore_files_leave_the_context(self):
        (self.dir / '.mddtignore').write_bytes(b'\xff\xfe*.md\n')
        self.assertIsNotNone(self.context('Edit', {'file_path': str(self.dir / 'doc.md'),
                                                   'old_string': 'Text.', 'new_string': '## Part\n'}))

    def test_write_compares_with_the_current_file(self):
        path = self.dir / 'doc.md'
        self.assertIsNotNone(self.context('Write', {'file_path': str(path), 'content': '# Doc\n\nText.\n'}))
        path.write_text('# Doc\n\n## A\n', encoding='utf-8')
        self.assertIsNone(self.context('Write', {'file_path': str(path), 'content': '# Doc\n\n## B\n'}))
        self.assertIsNotNone(self.context('Write', {'file_path': str(path), 'content': '# Doc\n\n## A\n\n## B\n'}))

    def test_codex_patch_adding_headings(self):
        patch = ('*** Begin Patch\n*** Update File: docs/guide.md\n@@\n-Old text.\n+Old text.\n+\n+## Setup\n'
                 '*** Add File: run.py\n+# comment\n*** End Patch\n')
        text = self.context('apply_patch', {'command': patch})
        self.assertIn('guide.md', text)
        self.assertNotIn('run.py', text)
        renamed = '*** Begin Patch\n*** Update File: a.md\n@@\n-## Old\n+## New\n*** End Patch\n'
        self.assertIsNone(self.context('apply_patch', {'command': renamed}))
        self.assertIsNone(self.context('apply_patch', {'command': 42}))


class Events(HookCase):
    def test_other_events_and_tools_pass(self):
        path = self.write('README.md')
        event = self.event('Read', {'file_path': str(path), 'limit': 5})
        self.assertIsNone(self.decide({**event, 'hook_event_name': 'PostToolUse'}))
        self.assertIsNone(self.decide(self.event('Edit', {'file_path': str(path)})))
        self.assertIsNone(self.decide(self.event('Grep', {'pattern': 'x', 'path': str(path)})))
        self.assertIsNone(self.decide(self.event('Bash', {})))
        self.assertIsNone(self.decide({**event, 'tool_input': 'head README.md'}))

    def test_input_is_read_as_utf8(self):
        result = subprocess.run([sys.executable, str(HOOK)], capture_output=True,
                                input=json.dumps(self.event('Write', {'file_path': str(self.dir / '문서.md'),
                                                                      'content': '# 제목\n'}),
                                                 ensure_ascii=False).encode('utf-8'),
                                env={**os.environ, 'PYTHONIOENCODING': 'latin-1', 'PYTHONUTF8': '0'})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('문서.md', json.loads(result.stdout)['hookSpecificOutput']['additionalContext'])

    def test_malformed_input_fails_open(self):
        for payload in ('', 'not json', '[1, 2]'):
            with self.subTest(payload=payload):
                result = run(payload)
                self.assertEqual(result.returncode, 0)
                self.assertEqual(result.stdout, '')


if __name__ == '__main__':
    unittest.main()
