# SPDX-FileCopyrightText: 2026 Taeha Shin
# SPDX-License-Identifier: MIT
"""Hook that keeps agents to the mddt skill's reading and writing procedures.

The skill asks agents to read a chosen file whole and to follow its writing
procedure when they change a document's structure.
Agents still preview entry documents and contributor guides with `head` or a
line range, and add sections without the procedure.
For Claude Code and Codex, this hook denies partial reads of those documents
and, when an edit adds a Markdown heading, points the agent to the skill.

It reads one PreToolUse event as JSON on stdin and prints its response as JSON on
stdout, or nothing to let the call proceed unchanged.
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

# The skill this script belongs to, named in messages so that an agent that has
# not loaded the skill can find it.
SKILL = Path(__file__).resolve().parents[1] / 'SKILL.md'

# ATX headings and code fences, which the heading count skips over.
HEADING = re.compile(r' {0,3}#{1,6}(?:[ \t]|$)')
FENCE = re.compile(r' {0,3}(`{3,}|~{3,})')

# Commands that print a file's contents.
READERS = frozenset(('cat', 'nl', 'bat', 'batcat', 'head', 'tail', 'sed', 'awk', 'gawk', 'more', 'less'))
# Shells whose `-c` script is judged like the command itself, as in Codex's `bash -lc`.
SHELLS = frozenset(('bash', 'sh', 'zsh', 'dash'))
SEPARATORS = frozenset((';', '&&', '||', '&', ';;'))
# An output redirection such as `>`, `>>`, or `2>`, whose next word is written, not read.
OUTPUT = re.compile(r'\d*>[>|]?')


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
    # A backslash before a line break continues the command on the next line.
    command = re.sub(r'\\\r?\n', ' ', command)
    # Descriptor duplication such as `2>&1` or `&>` is not a command separator.
    command = re.sub(r'(?<=[<>])&|&(?=>)', '', command)
    words = []
    # Lines end commands like semicolons, and each is split on its own; this also
    # splits multi-line quoted text, which only matters for the rare command that quotes a file name.
    for line in command.splitlines():
        lexer = shlex.shlex(line, posix=True, punctuation_chars=';&|<')
        lexer.whitespace_split = True
        # shlex starts a comment at any `#`, even inside a word, while the shell starts
        # one only at the start of a word, so comments are dropped below instead.
        lexer.commenters = ''
        try:
            line_words = list(lexer)
        except ValueError:
            line_words = re.findall(r'\|\||&&|[;|&<]|[^\s;|&<]+', line)
        for word in line_words:
            if word.startswith('#'):
                break
            words.append(word)
        words.append(';')
    return words


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
        # An in-place edit such as `sed -i` writes the file instead of printing it.
        if any(re.fullmatch(r'-[a-zA-Z]*i.*', arg) or arg.startswith('--in-place') for arg in args):
            return False
        quiet = any(arg in ('--quiet', '--silent') or re.fullmatch(r'-[a-zA-Z]*n[a-zA-Z]*', arg) for arg in args)
        # A quit command after a line number, such as `80q` or `1,5p;5q`, but not a
        # number followed by q inside a substitution such as `s/1 quarter/.../`.
        quits = any(re.search(r'(?:^|[;\s{])\d+\s*[qQ](?:$|[;\s}\d])', arg) for arg in args)
        return quiet or quits
    if name in ('awk', 'gawk'):
        # A condition on the line number, such as `NR<10`, rather than `print NR`.
        return any(re.search(r'\bNR\s*(?:[<>]=?|[!=]=)|(?:[<>]=?|[!=]=)\s*NR\b', arg) for arg in args)
    return False


def operands(args):
    """Yield a command's arguments, leaving out the targets of output redirections."""
    written = False
    for arg in args:
        if written:
            written = False
        elif OUTPUT.fullmatch(arg):
            written = True
        else:
            yield arg


def covered_file(args):
    """Return a covered file that a reading command takes as an argument or an input redirection."""
    for arg in operands(args):
        if not arg.startswith('-') and is_whole_file(arg):
            return arg
    return None


def shell_script(args):
    """Return the script of a shell's `-c` option, such as the one in `bash -lc 'head README.md'`."""
    for i, arg in enumerate(args):
        if re.fullmatch(r'-[a-zA-Z]*c[a-zA-Z]*', arg):
            return args[i + 1] if i + 1 < len(args) else None
    return None


def cut_whole_file(path, cwd):
    """Whether a truncated shell read of a covered file is denied.

    The file is found from the event's directory, not from a `cd` earlier in the
    command, and one that is not found there is still denied.
    """
    full = Path(cwd or '.') / path
    return not (full.is_file() and too_large(full))


def partial_shell_read(command, cwd=None):
    """Return the file name when a shell command prints part of a covered file."""
    for pipeline in pipelines(tokens(command)):
        read = None
        for simple in pipeline:
            name, args = program(simple)
            if name is None:
                continue
            if name in SHELLS:
                script = shell_script(args)
                found = partial_shell_read(script, cwd) if script else None
                if found:
                    return found
                read = None
            elif name not in READERS:
                # A filter such as grep shows search results, which may be cut, rather than the file.
                read = None
            else:
                read = covered_file(args) or read
                if read and truncates(name, args) and cut_whole_file(read, cwd):
                    return Path(read).name
    return None


def skill_intro():
    """Introduce the skill by its entry, so that an agent can load it."""
    if SKILL.is_file():
        return f'The mddt skill, whose entry is {SKILL}, governs the structure of Markdown documents.'
    return 'The mddt skill governs the structure of Markdown documents.'


def read_reason(name, tool):
    if tool == 'Read':
        how = 'Call Read again without offset or limit.'
    else:
        how = 'Read it with a tool that shows the whole file, such as Read, or print it whole with cat.'
    return (f'mddt: {name} is read whole. {skill_intro()} '
            'Its reading procedure, references/reading.md, asks for whole reads, '
            'and such documents decide what else to read or do, so a cut can hide a link or a requirement. '
            f'{how} Searching it with grep is still fine.')


def write_context(names):
    files = ', '.join(sorted(names))
    return (f'mddt: this edit adds a heading to {files}. {skill_intro()} '
            'Load it if it is not loaded, and follow its writing procedure, references/writing.md: '
            'place new content in the document tree, and once the content settles, '
            'reread each changed part or topic whole and run the checker.')


def headings(text):
    """Count ATX headings outside fenced code blocks."""
    count, fence = 0, None
    for line in text.splitlines():
        match = FENCE.match(line)
        if fence:
            if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence):
                fence = None
        elif match:
            fence = match.group(1)
        elif HEADING.match(line):
            count += 1
    return count


def is_markdown(path):
    return isinstance(path, str) and path.lower().endswith(('.md', '.markdown'))


def current_text(path, cwd):
    try:
        return (Path(cwd or '.') / path).read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError):
        return ''


def patch_headings(patch):
    """Return the Markdown files that a Codex patch adds headings to.

    The patch names each file on a line such as `*** Update File: path` or
    `*** Add File: path`, and prefixes added and removed lines with + and -.
    """
    added, removed, path = {}, {}, None
    for line in patch.splitlines():
        header = re.match(r'\*\*\* (?:Add|Update|Delete) File: (.+)', line)
        if header:
            path = header.group(1).strip()
            continue
        if not is_markdown(path) or line[:3] in ('+++', '---'):
            continue
        if line.startswith('+'):
            added[path] = added.get(path, '') + line[1:] + '\n'
        elif line.startswith('-'):
            removed[path] = removed.get(path, '') + line[1:] + '\n'
    return {Path(p).name for p in added if headings(added[p]) > headings(removed.get(p, ''))}


def added_headings(tool, tool_input, cwd):
    """Return the names of Markdown files that a write call adds headings to."""
    if tool == 'apply_patch':
        patch = tool_input.get('command')
        return patch_headings(patch) if isinstance(patch, str) else set()
    path = tool_input.get('file_path')
    if not is_markdown(path):
        return set()
    if tool == 'Edit':
        old, new = tool_input.get('old_string'), tool_input.get('new_string')
        grew = isinstance(old, str) and isinstance(new, str) and headings(new) > headings(old)
    elif tool == 'Write':
        content = tool_input.get('content')
        # Judged before the call runs, so the file still holds the earlier text.
        grew = isinstance(content, str) and headings(content) > headings(current_text(path, cwd))
    else:
        grew = False
    return {Path(path).name} if grew else set()


def decide(event):
    """Return the hook's response to an event, or None to let the call proceed unchanged."""
    if event.get('hook_event_name') != 'PreToolUse':
        return None
    tool = event.get('tool_name')
    tool_input = event.get('tool_input')
    if not isinstance(tool_input, dict):
        return None
    if tool in ('Edit', 'Write', 'apply_patch'):
        names = added_headings(tool, tool_input, event.get('cwd'))
        if not names:
            return None
        # Context without a permission decision lets the call proceed.
        return {'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'additionalContext': write_context(names)}}
    if tool == 'Read':
        name = partial_read(tool_input, event.get('cwd'))
    elif tool == 'Bash':
        command = tool_input.get('command')
        if isinstance(command, list):
            # Quoting keeps each part one word, such as the script of `bash -lc`.
            command = shlex.join(str(part) for part in command)
        name = partial_shell_read(command, event.get('cwd')) if isinstance(command, str) else None
    else:
        return None
    if name is None:
        return None
    return {'hookSpecificOutput': {
        'hookEventName': 'PreToolUse',
        'permissionDecision': 'deny',
        'permissionDecisionReason': read_reason(name, tool),
    }}


def main():
    try:
        # Hosts send UTF-8, which the locale encoding of a Windows console may not be.
        event = json.load(sys.stdin.buffer)
        decision = decide(event) if isinstance(event, dict) else None
    except Exception as error:  # Fail open: a hook that cannot judge must not block.
        print(f'mddt hook skipped: {type(error).__name__}', file=sys.stderr)
        return 0
    if decision:
        json.dump(decision, sys.stdout)
    return 0


if __name__ == '__main__':
    sys.exit(main())
