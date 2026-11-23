# SPDX-FileCopyrightText: 2026 Taeha Shin
# SPDX-License-Identifier: MIT
"""Behavioral checks of the read-whole hook through its event interface."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / 'skills/mddt/scripts/read_whole.py'


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

    def decide(self, payload):
        result = run(payload)
        self.assertEqual(result.returncode, 0, result.stderr)
        if not result.stdout:
            return None
        output = json.loads(result.stdout)['hookSpecificOutput']
        self.assertEqual(output['hookEventName'], 'PreToolUse')
        self.assertEqual(output['permissionDecision'], 'deny')
        return output['permissionDecisionReason']

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
                        "awk '{print $1}' README.md", 'echo README.md; head -3 notes.md'):
            with self.subTest(command=command):
                self.assertIsNone(self.shell(command))

    def test_unbalanced_quotes_fall_back_to_words(self):
        self.assertIsNotNone(self.shell("head -80 README.md; echo 'unclosed"))

    def test_command_given_as_a_list(self):
        self.assertIsNotNone(self.decide(self.event('Bash', {'command': ['head', '-5', 'README.md']})))


class Events(HookCase):
    def test_other_events_and_tools_pass(self):
        path = self.write('README.md')
        event = self.event('Read', {'file_path': str(path), 'limit': 5})
        self.assertIsNone(self.decide({**event, 'hook_event_name': 'PostToolUse'}))
        self.assertIsNone(self.decide(self.event('Edit', {'file_path': str(path)})))
        self.assertIsNone(self.decide(self.event('Bash', {})))
        self.assertIsNone(self.decide({**event, 'tool_input': 'head README.md'}))

    def test_malformed_input_fails_open(self):
        for payload in ('', 'not json', '[1, 2]'):
            with self.subTest(payload=payload):
                result = run(payload)
                self.assertEqual(result.returncode, 0)
                self.assertEqual(result.stdout, '')


if __name__ == '__main__':
    unittest.main()
