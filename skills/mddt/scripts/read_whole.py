# SPDX-FileCopyrightText: 2026 Taeha Shin
# SPDX-License-Identifier: MIT
"""PreToolUse hook that stops partial reads of documents agents must read whole.

The reading procedure asks agents to read a chosen file whole.
Agents still preview entry documents and contributor guides with `head` or a
line range, and miss what lies below the cut.
This hook denies such reads for Claude Code and Codex and asks for a whole read.

It reads one PreToolUse event as JSON on stdin and prints a denial as JSON on
stdout, or nothing to let the call proceed.
Any error lets the call proceed, so the hook never blocks work it cannot judge.
Only the Python standard library is used, so the hook starts quickly.
"""
import json
import os
from pathlib import Path
import re
import shlex
import sys

# Files compared by name, case-insensitively: every README, the agent entries
# that tools read by name, and contributor guidance.
WHOLE_FILES = frozenset(name.lower() for name in (
    'README.md', 'CONTRIBUTING.md', 'SKILL.md', 'AGENTS.md', 'CLAUDE.md', 'GEMINI.md'))

# A file this large cannot be read at once, so the reading procedure divides it
# at topic boundaries and the hook lets ranged reads through.
MAX_WHOLE_BYTES = 256 * 1024
MAX_WHOLE_LINES = 2000

# Commands that print a file's contents.
READERS = frozenset(('cat', 'nl', 'bat', 'batcat', 'head', 'tail', 'sed', 'awk', 'gawk', 'more', 'less'))
SEPARATORS = frozenset((';', '&&', '||', '&', ';;'))


def is_whole_file(path):
    return Path(path).name.lower() in WHOLE_FILES


def too_large(path):
    """Whether the file exceeds what a single read holds, or cannot be inspected."""
    try:
        if os.path.getsize(path) > MAX_WHOLE_BYTES:
            return True
        with open(path, 'rb') as handle:
            return sum(1 for _ in handle) > MAX_WHOLE_LINES
    except OSError:
        return True


def line_count(path):
    with open(path, 'rb') as handle:
        return sum(1 for _ in handle)


def partial_read(tool_input, cwd):
    """Return the file name when a Read call leaves part of a covered file unread."""
    path = tool_input.get('file_path')
    if not isinstance(path, str) or not is_whole_file(path):
        return None
    offset, limit = tool_input.get('offset'), tool_input.get('limit')
    if offset is None and limit is None:
        return None
    full = Path(cwd or '.') / path
    if too_large(full):
        return None
    # A range that starts at the first line and reaches the last is a whole read.
    starts_at_top = offset in (None, 0, 1)
    if starts_at_top and (limit is None or limit >= line_count(full)):
        return None
    return Path(path).name


def tokens(command):
    """Split a shell command into words and control operators.

    Quoting errors fall back to splitting at spaces and operators, which still finds plain
    commands such as `head -80 README.md`.
    """
    # Lines end commands like semicolons; this also splits multi-line quoted
    # text, which only matters for the rare command that quotes a file name.
    command = command.replace('\n', ' ; ')
    # Descriptor duplication such as `2>&1` or `&>` is not a command separator.
    command = re.sub(r'(?<=[<>])&|&(?=>)', '', command)
    lexer = shlex.shlex(command, posix=True, punctuation_chars=';&|<')
    lexer.whitespace_split = True
    try:
        return list(lexer)
    except ValueError:
        return re.findall(r'\|\||&&|[;|&<]|[^\s;|&<]+', command)


def pipelines(words):
    """Group words into pipelines, each a list of simple commands."""
    current, command = [], []
    for word in words:
        if word in SEPARATORS:
            current.append(command)
            yield current
            current, command = [], []
        elif word == '|':
            current.append(command)
            command = []
        else:
            command.append(word)
    current.append(command)
    yield current


def program(command):
    """Return the command name and its arguments, skipping variable assignments."""
    words = [word for word in command if word]
    while words and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*=.*', words[0]):
        words = words[1:]
    if not words:
        return None, []
    return Path(words[0]).name, words[1:]


def truncates(name, args):
    """Whether a command prints only part of its input."""
    if name in ('head', 'tail'):
        return True
    if name == 'sed':
        return any(arg == '-n' or re.fullmatch(r'-[a-zA-Z]*n[a-zA-Z]*', arg) for arg in args) or any(
            re.search(r'\d\s*q', arg) for arg in args)
    if name in ('awk', 'gawk'):
        return any('NR' in arg for arg in args)
    return False


def covered_file(name, args):
    """Return a covered file that a reading command takes as an argument."""
    if name not in READERS:
        return None
    for arg in args:
        if not arg.startswith('-') and is_whole_file(arg):
            return Path(arg).name
    return None


def partial_shell_read(command):
    """Return the file name when a shell command prints part of a covered file."""
    for pipeline in pipelines(tokens(command)):
        read = None
        for simple in pipeline:
            name, args = program(simple)
            if name is None:
                continue
            for i, arg in enumerate(args):
                # An input redirection such as `head -5 < README.md`.
                if arg == '<' and i + 1 < len(args) and is_whole_file(args[i + 1]):
                    read = read or Path(args[i + 1]).name
                    if truncates(name, args):
                        return read
            target = covered_file(name, args)
            if target and truncates(name, args):
                return target
            if read and truncates(name, args):
                return read
            read = read or target
    return None


def reason(name, tool):
    if tool == 'Read':
        how = 'Call Read again without offset or limit.'
    else:
        how = 'Read it with a tool that shows the whole file, such as Read, or print it whole with cat.'
    return (f'mddt: {name} is a document that agents read whole, because what lies below a cut '
            f'can change what else to read or do. {how} '
            'Searching it with grep is still fine.')


def decide(event):
    """Return a denial for a PreToolUse event, or None to let the call proceed."""
    if event.get('hook_event_name') != 'PreToolUse':
        return None
    tool = event.get('tool_name')
    tool_input = event.get('tool_input')
    if not isinstance(tool_input, dict):
        return None
    if tool == 'Read':
        name = partial_read(tool_input, event.get('cwd'))
    elif tool == 'Bash':
        command = tool_input.get('command')
        if isinstance(command, list):
            command = ' '.join(str(part) for part in command)
        name = partial_shell_read(command) if isinstance(command, str) else None
    else:
        return None
    if name is None:
        return None
    return {'hookSpecificOutput': {
        'hookEventName': 'PreToolUse',
        'permissionDecision': 'deny',
        'permissionDecisionReason': reason(name, tool),
    }}


def main():
    try:
        event = json.load(sys.stdin)
        decision = decide(event) if isinstance(event, dict) else None
    except Exception as error:  # Fail open: a hook that cannot judge must not block.
        print(f'mddt read-whole hook skipped: {type(error).__name__}', file=sys.stderr)
        return 0
    if decision:
        json.dump(decision, sys.stdout)
    return 0


if __name__ == '__main__':
    sys.exit(main())
