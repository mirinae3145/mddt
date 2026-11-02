#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["markdown-it-py>=3", "mdit-py-plugins>=0.4"]
# ///
"""Check Markdown files against the mddt document-tree model.

The checker reports only the outer boundary of the model: violations a parser
can decide (errors) and signals that need a writer's judgment (warnings).
Choosing between sections, lists, and tables inside that boundary is left to
the writer.

Detection metadata lives in rules.toml and fix guidance in fixes.toml, so that
this file holds only detection logic.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import fnmatch
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tomllib
from urllib.parse import unquote

from markdown_it import MarkdownIt
from markdown_it.tree import SyntaxTreeNode
from mdit_py_plugins.front_matter import front_matter_plugin

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
FIXES = SCRIPT_DIR / 'fixes.toml'
REGISTRY = SCRIPT_DIR / 'rules.toml'

LIST_TYPES = {'bullet_list', 'ordered_list'}
# Blocks that neither introduce nor interrupt content, such as comments.
TRANSPARENT = {'html_block', 'front_matter'}
GROUP_ORDER = {'structure': 0, 'sentence': 1}
SEVERITY_ORDER = {'error': 0, 'warning': 1, 'info': 2}
MAX_LIST_ITEMS = 7
NAME_MAX_WORDS = 6
# MD036 treats emphasis ending in punctuation as a sentence, not a heading.
HEADING_PUNCTUATION = '.,;:!?。，；：！？'
COLON_NAME = re.compile(r'^(?P<name>[^:：\n]{1,40}?)[:：](?:\s|$)')
LINK_NAME_TAIL = re.compile(r'^\s*(?:[:：—–]|-\s)')
CONVENTION_FILES = re.compile(r'^changelog(\..*)?$', re.IGNORECASE)

# A folder's index file is the parent of the folder's other documents.
INDEX_NAMES = ('readme.md', 'index.md', 'skill.md')
# Tools read these files by name, so they need no parent document.
ENTRY_NAMES = {'skill.md', 'agents.md', 'claude.md', 'gemini.md'}
URL_SCHEME = re.compile(r'^[a-z][a-z0-9+.-]*:', re.IGNORECASE)

# Provisional thresholds for review information, to be calibrated against
# documents written to the model.
SIBLING_RATIO = 3
SIBLING_MIN_LINES = 20
FILE_MAX_LINES = 300

MAX_SENTENCES = 5
MAX_PARAGRAPH_RUN = 3
MAX_WORDS = 25
# Prose keeps one sentence per line, so a sentence ends where a line ends with
# sentence punctuation; a colon ends the sentence that introduces a list.
SENTENCE_END = re.compile(r'[.!?。！？:：][\'"”’)\]*_]*$')
CONTAINER_PREFIX = re.compile(r'^\s*(?:>\s?)*(?:[-*+]\s+|\d+[.)]\s+)?')
COMMENT = re.compile(r'<!--.*?-->')
BOUNDARY = re.compile(r'([.!?。！？])([\'"”’)\]*_]*)\s+([\'"“‘(*_]*)(\S)')
ABBREVIATIONS = {'e.g', 'i.e', 'etc', 'vs', 'cf', 'al', 'fig', 'no', 'dr', 'mr', 'mrs', 'ms', 'st', 'approx'}

KIND = {
    'heading': 'a heading',
    'table': 'a table',
    'fence': 'a code block',
    'code_block': 'a code block',
    'bullet_list': 'another list',
    'ordered_list': 'another list',
    'blockquote': 'a block quote',
    'hr': 'a thematic break',
    'paragraph': 'a paragraph',
}


@dataclass
class Diagnostic:
    path: str
    line: int
    end_line: int
    code: str
    detail: str


@dataclass
class Heading:
    index: int
    level: int
    text: str
    line: int
    node: SyntaxTreeNode
    region: list[SyntaxTreeNode] = field(default_factory=list)
    is_topic: bool = False
    h3_count: int = 0


def load_registry() -> dict[str, dict]:
    with REGISTRY.open('rb') as f:
        registry = tomllib.load(f)
    for code, entry in registry.items():
        for key in ('severity', 'group', 'summary', 'rule'):
            if key not in entry:
                raise SystemExit(f'mddt: registry entry {code} lacks {key}')
    return registry


def load_fixes() -> dict[str, str]:
    with FIXES.open('rb') as f:
        return tomllib.load(f)


def parser() -> MarkdownIt:
    return MarkdownIt('commonmark').enable('table').use(front_matter_plugin)


def start_line(node: SyntaxTreeNode) -> int:
    return node.map[0] + 1 if node.map else 1


def end_line(node: SyntaxTreeNode) -> int:
    return node.map[1] if node.map else start_line(node)


def inline_children(block: SyntaxTreeNode) -> list[SyntaxTreeNode]:
    """Return the inline nodes of a paragraph or heading, without empty text."""
    if not block.children or block.children[0].type != 'inline':
        return []
    return [n for n in block.children[0].children
            if not (n.type == 'text' and not n.content)]


def plain_text(node: SyntaxTreeNode) -> str:
    if node.type in ('text', 'code_inline'):
        return node.content
    if node.type == 'softbreak':
        return ' '
    return ''.join(plain_text(c) for c in node.children)


def block_text(block: SyntaxTreeNode) -> str:
    return ''.join(plain_text(n) for n in inline_children(block)).strip()


def is_badge_paragraph(block: SyntaxTreeNode) -> bool:
    """A paragraph of images or image links, such as README badges."""
    nodes = inline_children(block)
    if not nodes:
        return False
    for n in nodes:
        if n.type == 'image' or n.type == 'softbreak':
            continue
        if n.type == 'text' and not n.content.strip():
            continue
        if n.type == 'link' and n.children and all(c.type == 'image' for c in n.children):
            continue
        return False
    return True


def meaningful(blocks: list[SyntaxTreeNode]) -> list[SyntaxTreeNode]:
    return [b for b in blocks if b.type not in TRANSPARENT]


def overview_problem(heading: Heading) -> str | None:
    """Describe why the heading's region does not open with an overview."""
    for block in meaningful(heading.region):
        if block.type == 'paragraph' and is_badge_paragraph(block):
            continue
        if block.type == 'paragraph':
            return None
        return f'is followed by {KIND.get(block.type, block.type)} instead of an overview paragraph'
    return 'has no overview paragraph before the next heading'


def name_of(item: SyntaxTreeNode) -> tuple[str, str] | None:
    """Return (form, name) when a list item opens with a name.

    A name is whatever calls out what the item is about: a bold term, a short
    phrase followed by a colon, or link text followed by a separator.
    """
    if not item.children or item.children[0].type != 'paragraph':
        return None
    nodes = inline_children(item.children[0])
    if not nodes:
        return None
    first = nodes[0]
    if first.type == 'strong':
        return 'bold', plain_text(first).strip()
    if first.type == 'link':
        rest = nodes[1] if len(nodes) > 1 else None
        if rest is None or (rest.type == 'text' and LINK_NAME_TAIL.match(rest.content)):
            return 'link', plain_text(first).strip()
        return None
    lead = ''
    for n in nodes:
        if n.type not in ('text', 'code_inline'):
            break
        lead += n.content
    match = COLON_NAME.match(lead)
    if match and len(match['name'].split()) <= NAME_MAX_WORDS:
        return 'colon', match['name'].strip()
    return None


def item_key(item: SyntaxTreeNode) -> str:
    named = name_of(item)
    if named:
        return named[1]
    if item.children and item.children[0].type == 'paragraph':
        return block_text(item.children[0])
    return ''


def is_mechanically_ordered(items: list[SyntaxTreeNode]) -> bool:
    """True when items are sorted by name or number, in either direction.

    Such lists can be scanned without understanding their content, so their
    length is not a structural problem.
    """
    keys = [item_key(i) for i in items]
    if not all(keys):
        return False
    if all(re.match(r'\d', k) for k in keys):
        values = [tuple(int(x) for x in re.findall(r'\d+', k)) for k in keys]
    else:
        values = [k.casefold() for k in keys]
    return values == sorted(values) or values == sorted(values, reverse=True)


def is_heading_like_emphasis(block: SyntaxTreeNode) -> bool:
    if block.type != 'paragraph' or end_line(block) - start_line(block) > 0:
        return False
    nodes = [n for n in inline_children(block)
             if not (n.type == 'text' and not n.content.strip())]
    if len(nodes) != 1 or nodes[0].type not in ('strong', 'em'):
        return False
    text = plain_text(nodes[0]).strip()
    return bool(text) and text[-1] not in HEADING_PUNCTUATION


def clean_prose(line: str, placeholder: str = '') -> str:
    """Remove what does not count as prose: comments, code, link targets, and URLs.

    With a placeholder, code spans become a single token and link text loses its
    sentence punctuation, which keeps sentence boundaries around them detectable.
    """
    line = COMMENT.sub(' ', line)
    line = re.sub(r'`[^`]*`', f' {placeholder} ' if placeholder else ' ', line)
    line = re.sub(r'!\[([^\]]*)\]\([^)]*\)', ' ', line)
    # Link text counts as words, but punctuation inside a link never ends a sentence.
    line = re.sub(r'\[([^\]]*)\]\([^)]*\)',
                  lambda m: re.sub(r'[.!?。！？]', '', m.group(1)) if placeholder else m.group(1), line)
    line = re.sub(r'<https?://[^>]*>|https?://\S+|<[^>]+>', ' ', line)
    return line


def count_words(text: str) -> int:
    return sum(1 for token in text.split() if re.search(r'\w', token))


def sentence_breaks(line: str) -> list[int]:
    """Return positions inside a line where a new sentence starts.

    A boundary needs sentence punctuation, whitespace, and a new sentence:
    Korean text ending a sentence, or an uppercase letter after Latin text.
    Abbreviations and single-letter initials are not boundaries.
    """
    breaks = []
    for m in BOUNDARY.finditer(line):
        word = re.search(r'(\S+)$', line[:m.start(1)])
        previous = word.group(1) if word else ''
        if not previous or previous.lower().rstrip('.') in ABBREVIATIONS:
            continue
        if re.fullmatch(r'[A-Z]', previous) or re.search(r'\.\w$', previous):
            continue
        hangul = '\uac00' <= previous[-1] <= '\ud7a3'
        if hangul or m.group(1) in '。！？' or (m.group(4).isupper() and m.group(4).isalpha()):
            breaks.append(m.start(3))
    return breaks


def github_slug(text: str) -> str:
    return re.sub(r'[^\w\- ]', '', text.strip().lower()).replace(' ', '-')


class FileCheck:
    def __init__(self, path: str, text: str):
        self.path = path
        self.lines = text.splitlines()
        self.line_count = len(self.lines)
        self.root = SyntaxTreeNode(parser().parse(text))
        self.blocks = list(self.root.children)
        self.diagnostics: list[Diagnostic] = []
        self.headings = self._headings()

    def report(self, code: str, node_or_line, detail: str) -> None:
        if isinstance(node_or_line, int):
            line = last = node_or_line
        else:
            line, last = start_line(node_or_line), end_line(node_or_line)
        self.diagnostics.append(Diagnostic(self.path, line, max(line, last), code, detail))

    def _headings(self) -> list[Heading]:
        headings = [Heading(i, int(b.tag[1]), block_text(b), start_line(b), b)
                    for i, b in enumerate(self.blocks) if b.type == 'heading']
        for k, h in enumerate(headings):
            stop = headings[k + 1].index if k + 1 < len(headings) else len(self.blocks)
            h.region = self.blocks[h.index + 1:stop]
        for k, h in enumerate(headings):
            if h.level != 2:
                continue
            for later in headings[k + 1:]:
                if later.level <= 2:
                    break
                if later.level == 3:
                    h.h3_count += 1
            h.is_topic = h.h3_count > 0
        return headings

    def scope_of(self, index: int) -> str:
        """Name-form scope: a topic H2 with its H3s, or the parent's own parts."""
        owner = None
        for h in self.headings:
            if h.index > index:
                break
            if h.level <= 2:
                owner = h
        if owner and owner.level == 2 and owner.is_topic:
            return f'topic "{owner.text}"'
        return 'the parent topic'

    def run(self) -> list[Diagnostic]:
        self.check_headings()
        self.check_regions()
        self.check_lists()
        self.check_prose()
        self.check_sizes()
        return self.diagnostics

    def check_sizes(self) -> None:
        if self.line_count > FILE_MAX_LINES:
            self.report('file-size', 1, f'file has {self.line_count} lines')
        groups: dict[tuple[int, int], list[int]] = {}
        for k, h in enumerate(self.headings):
            owner = next((j for j in range(k - 1, -1, -1) if self.headings[j].level < h.level), -1)
            groups.setdefault((owner, h.level), []).append(k)
        for siblings in groups.values():
            if len(siblings) < 2:
                continue
            sizes = {k: self.section_lines(k) for k in siblings}
            for k, size in sizes.items():
                others = sorted(v for j, v in sizes.items() if j != k)
                median = others[len(others) // 2]
                if size >= SIBLING_MIN_LINES and size >= SIBLING_RATIO * max(median, 1):
                    h = self.headings[k]
                    self.report('sibling-imbalance', h.node,
                                f'"{h.text}" has {size} lines; its siblings have a median of {median}')

    def sentences(self, paragraph: SyntaxTreeNode) -> list[tuple[int, int]]:
        """Return (first line, word count) for each sentence of a paragraph.

        Sentences are counted across line breaks until a line ends with
        sentence punctuation, so breaking a long sentence over several lines
        does not hide its length.
        """
        found, words, start = [], 0, None
        first, last = paragraph.map
        for no in range(first, last):
            raw = self.lines[no]
            raw = CONTAINER_PREFIX.sub('', raw) if no == first else re.sub(r'^\s*(?:>\s?)*', '', raw)
            text = clean_prose(raw, placeholder='X')
            # Sentences that end inside a line, as in hard-wrapped text, also end here.
            pieces = [text[a:b] for a, b in zip([0] + sentence_breaks(text),
                                                sentence_breaks(text) + [len(text)])]
            for k, piece in enumerate(pieces):
                if k:
                    if start is not None:
                        found.append((start, words))
                    words, start = 0, None
                n = count_words(piece.replace(' X ', ' '))
                if n and start is None:
                    start = no + 1
                words += n
            if SENTENCE_END.search(COMMENT.sub('', raw).rstrip()) or no == last - 1:
                if start is not None:
                    found.append((start, words))
                words, start = 0, None
        return found

    def check_prose(self) -> None:
        for node in self.root.walk():
            if node.type != 'paragraph' or not node.map or is_badge_paragraph(node):
                continue
            first, last = node.map
            for no in range(first, last):
                text = clean_prose(CONTAINER_PREFIX.sub('', self.lines[no]), placeholder='X')
                if sentence_breaks(text):
                    self.report('line-sentences', no + 1, 'line holds more than one sentence')
            found = self.sentences(node)
            if len(found) > MAX_SENTENCES:
                self.report('paragraph-length', node, f'paragraph has {len(found)} sentences')
            for line, words in found:
                if words > MAX_WORDS:
                    self.report('sentence-length', line, f'sentence has {words} words')
        run: list[SyntaxTreeNode] = []
        for block in self.blocks + [None]:
            if block is not None and block.type in TRANSPARENT:
                continue
            if block is not None and block.type == 'paragraph':
                run.append(block)
                continue
            if len(run) > MAX_PARAGRAPH_RUN:
                self.report('paragraph-run', run[0], f'{len(run)} paragraphs in a row')
            run = []

    def links(self) -> list[tuple[str, int, bool]]:
        """Return (target, line, alone) for every link in the file.

        A link is alone when nothing but punctuation surrounds it in its
        paragraph, list item, or table cell, so it carries no summary.
        """
        found = []
        line = 1
        for node in self.root.walk():
            if not node.is_root and node.map:
                line = start_line(node)
            if node.type != 'inline':
                continue
            parts = [n for n in node.children if n.type != 'softbreak']
            for n in node.walk():
                if n.type == 'link':
                    alone = all(o is n or (o.type == 'text' and not re.search(r'\w', o.content))
                                for o in parts)
                    found.append((n.attrs.get('href', ''), line, alone))
        return found

    def anchors(self) -> dict[str, Heading]:
        """Map GitHub-style heading anchors, with suffixes for duplicates, to headings."""
        found: dict[str, Heading] = {}
        counts: dict[str, int] = {}
        for h in self.headings:
            slug = github_slug(h.text)
            n = counts.get(slug, 0)
            counts[slug] = n + 1
            found[f'{slug}-{n}' if n else slug] = h
        return found

    def check_headings(self) -> None:
        h1s = [h for h in self.headings if h.level == 1]
        if not h1s:
            self.report('h1-missing', 1, 'no level-1 heading')
        for extra in h1s[1:]:
            self.report('h1-multiple', extra.node, f'another level-1 heading "{extra.text}"')
        for h in h1s:
            problem = overview_problem(h)
            if problem:
                self.report('h1-overview', h.node, f'"{h.text}" {problem}')
        previous = None
        seen_topic = None
        # Parts after a topic share one cause, so they are reported once per run.
        late_parts: list[Heading] = []
        for h in self.headings:
            if previous and h.level > previous.level + 1:
                self.report('heading-skip', h.node,
                            f'H{previous.level} is followed by H{h.level} "{h.text}"')
            if h.level >= 4:
                self.report('heading-depth', h.node, f'H{h.level} "{h.text}"')
            if h.level == 1 or (h.level == 2 and h.is_topic):
                self.report_late_parts(late_parts, seen_topic)
                late_parts = []
            if h.level == 1:
                seen_topic = None
            if h.level == 2:
                if h.is_topic:
                    seen_topic = h
                    problem = overview_problem(h)
                    if problem:
                        self.report('topic-overview', h.node, f'"{h.text}" {problem}')
                    if h.h3_count == 1:
                        self.report('topic-single-child', h.node, f'"{h.text}" has one H3')
                elif seen_topic:
                    late_parts.append(h)
            previous = h
        self.report_late_parts(late_parts, seen_topic)

    def report_late_parts(self, parts: list[Heading], topic: Heading | None) -> None:
        if not parts or topic is None:
            return
        detail = f'part "{parts[0].text}" follows topic "{topic.text}"'
        if len(parts) > 1:
            detail += f', followed by {len(parts) - 1} more part(s)'
        self.report('part-after-topic', parts[0].node, detail)

    def check_regions(self) -> None:
        for block in self.blocks:
            if is_heading_like_emphasis(block):
                self.report('bold-heading', block, f'"{block_text(block)}"')
        for h in self.headings:
            self.check_list_intros(h)

    def check_list_intros(self, h: Heading) -> None:
        blocks = meaningful(h.region)
        needs_overview = h.level == 1 or (h.level == 2 and h.is_topic)
        for pos, block in enumerate(blocks):
            if block.type not in LIST_TYPES:
                continue
            previous = blocks[pos - 1] if pos else None
            if previous is not None and previous.type == 'paragraph':
                continue
            if previous is None and needs_overview:
                continue  # The missing overview is reported for the heading.
            if previous is None and len(blocks) == 1 and h.level >= 2:
                continue  # The heading introduces a list that is its only content.
            kind = KIND.get(previous.type, previous.type) if previous else 'the heading'
            self.report('list-intro', start_line(block), f'list follows {kind}')

    def check_lists(self) -> None:
        forms: dict[str, dict[str, list[int]]] = {}
        for index, block in enumerate(self.blocks):
            if block.type not in LIST_TYPES:
                continue
            deepest: dict[int, SyntaxTreeNode] = {}
            self.walk_list(block, 1, deepest, forms.setdefault(self.scope_of(index), {}))
            depth = max(deepest)
            if depth >= 4:
                self.report('list-depth-4', deepest[depth], f'list reaches depth {depth}')
            elif depth == 3:
                self.report('list-depth-3', deepest[3], 'list reaches depth 3')
        for scope, by_form in forms.items():
            if len(by_form) < 2:
                continue
            counts = ', '.join(f'{form} {len(lines)}' for form, lines in by_form.items())
            majority = max(by_form, key=lambda f: len(by_form[f]))
            first_other = min(line for f, lines in by_form.items() if f != majority for line in lines)
            self.report('name-form-mix', first_other, f'{scope} mixes name forms ({counts})')

    def walk_list(self, node: SyntaxTreeNode, depth: int,
                  deepest: dict[int, SyntaxTreeNode], forms: dict[str, list[int]]) -> None:
        deepest.setdefault(depth, node)
        items = [c for c in node.children if c.type == 'list_item']
        # A single nested item still marks a detail or exception of its parent.
        if len(items) == 1 and depth == 1:
            self.report('list-single', node, 'list has one item')
        if len(items) > MAX_LIST_ITEMS and not is_mechanically_ordered(items):
            self.report('list-length', node, f'{len(items)} items without mechanical order')
        for item in items:
            named = name_of(item)
            if named:
                forms.setdefault(named[0], []).append(start_line(item))
                descendant = first_named_descendant(item)
                if descendant:
                    self.report('name-nesting', item,
                                f'"{named[1]}" has named descendant "{descendant[1]}" '
                                f'at line {descendant[0]}')
            for child in item.children:
                if child.type in LIST_TYPES:
                    self.walk_list(child, depth + 1, deepest, forms)

    def section_lines(self, k: int) -> int:
        """Lines from a heading to the next heading of the same or a higher level.

        Comparing these sizes among sibling headings shows when one sibling
        holds content of a different level of detail.
        """
        h = self.headings[k]
        for later in self.headings[k + 1:]:
            if later.level <= h.level:
                return later.line - h.line
        return self.line_count - h.line + 1

    def outline(self) -> list[str]:
        lines = [self.path]
        for k, h in enumerate(self.headings):
            label = f'{"  " * (h.level - 1)}H{h.level} {h.text}'
            notes = [f'{self.section_lines(k)} lines']
            if h.level == 2:
                notes.append('topic' if h.is_topic else 'part')
            if h.level == 1 or (h.level == 2 and h.is_topic):
                notes.append('no overview' if overview_problem(h) else 'overview')
            stats = region_list_stats(h.region)
            if stats:
                notes.append(stats)
            lines.append(f'{label}  [{"; ".join(notes)}]')
        return lines


def index_file(folder: Path, skip: Path | None = None) -> Path | None:
    try:
        names = {p.name.lower(): p for p in folder.iterdir() if p.is_file()}
    except OSError:
        return None
    for name in INDEX_NAMES:
        found = names.get(name)
        if found and found != skip:
            return found
    return None


def folder_owner(folder: Path, root: Path) -> Path | None:
    """Return the document that owns a folder without its own index file.

    A companion file x.md owns the folder x/ beside it; otherwise the owner is
    the index file of the next folder up, repeated until the root.
    """
    while folder != root and root in folder.parents:
        companion = folder.with_name(folder.name + '.md')
        if companion.is_file():
            return companion
        folder = folder.parent
        found = index_file(folder)
        if found:
            return found
    return None


def parent_of(doc: Path, root: Path) -> Path | None:
    if index_file(doc.parent) == doc:
        return folder_owner(doc.parent, root)
    return index_file(doc.parent, skip=doc) or folder_owner(doc.parent, root)


def link_target(source: Path, href: str) -> Path | None:
    """Resolve a link to a local file path, without following symbolic links."""
    if not href or href.startswith('#') or URL_SCHEME.match(href):
        return None
    path = unquote(href.split('#')[0].split('?')[0])
    if not path:
        return None
    base = Path('/') if path.startswith('/') else source.parent
    target = Path(os.path.normpath(base / path))
    if target.is_dir():
        target = index_file(target) or target
    return target


def find_root(path: Path) -> Path | None:
    for folder in path.parents:
        if (folder / '.git').exists():
            return folder
    return None


class Tree:
    """Documents around the checked files, for checks that span files."""

    def __init__(self):
        self.cache: dict[Path, FileCheck | None] = {}

    def load(self, path: Path) -> FileCheck | None:
        if path not in self.cache:
            try:
                self.cache[path] = FileCheck(str(path), path.read_text(encoding='utf-8'))
            except (OSError, UnicodeDecodeError):
                self.cache[path] = None
        return self.cache[path]

    def check(self, path: Path, check: FileCheck, root: Path | None) -> None:
        self.check_anchors(path, check)
        if root is not None:
            self.check_parent(path, check, root)
            self.check_summaries(path, check, root)

    def check_summaries(self, path: Path, check: FileCheck, root: Path) -> None:
        """Report children whose every link from this parent lacks a summary."""
        bare: dict[Path, int] = {}
        summarized: set[Path] = set()
        for href, line, alone in check.links():
            target = link_target(path, href)
            if target is None or target == path or not target.is_file():
                continue
            if target.suffix.lower() != '.md' or parent_of(target, root) != path:
                continue
            if alone:
                bare.setdefault(target, line)
            else:
                summarized.add(target)
        for target, line in bare.items():
            if target not in summarized:
                check.report('link-without-summary', line,
                             f'link to child {relative(target, path)} has no summary')

    def check_anchors(self, path: Path, check: FileCheck) -> None:
        for href, line, _ in check.links():
            if '#' not in href:
                continue
            target = link_target(path, href)
            if target is None or target == path or target.suffix.lower() != '.md':
                continue
            other = self.load(target)
            if other is None:
                continue
            heading = other.anchors().get(unquote(href.split('#', 1)[1]))
            if heading and (heading.level >= 3 or (heading.level == 2 and not heading.is_topic)):
                check.report('anchor-to-part', line,
                             f'links to part "{heading.text}" in {relative(target, path)}')

    def check_parent(self, path: Path, check: FileCheck, root: Path) -> None:
        if path.name.lower() in ENTRY_NAMES or path == index_file(root):
            return
        parent = parent_of(path, root)
        if parent is None:
            return
        source = self.load(parent)
        if source is None:
            return
        if not any(link_target(parent, href) == path for href, _, _ in source.links()):
            check.report('doc-unlinked', 1, f'parent {relative(parent, path)} does not link here')


def relative(target: Path, source: Path) -> str:
    return os.path.relpath(target, source.parent)


def first_named_descendant(item: SyntaxTreeNode) -> tuple[int, str] | None:
    for child in item.children:
        if child.type not in LIST_TYPES:
            continue
        for sub in child.children:
            named = name_of(sub)
            if named:
                return start_line(sub), named[1]
            found = first_named_descendant(sub)
            if found:
                return found
    return None


def region_list_stats(region: list[SyntaxTreeNode]) -> str:
    depth = 0
    forms: dict[str, int] = {}

    def walk(node: SyntaxTreeNode, d: int) -> None:
        nonlocal depth
        depth = max(depth, d)
        for item in node.children:
            named = name_of(item)
            if named:
                forms[named[0]] = forms.get(named[0], 0) + 1
            for child in item.children:
                if child.type in LIST_TYPES:
                    walk(child, d + 1)

    for block in region:
        if block.type in LIST_TYPES:
            walk(block, 1)
    if not depth:
        return ''
    text = f'list depth {depth}'
    if forms:
        text += ', names ' + ', '.join(f'{f} {n}' for f, n in forms.items())
    return text


def collect(paths: list[str], excludes: list[str]) -> tuple[list[tuple[Path, Path | None]], list[str]]:
    """Expand arguments into Markdown files, each with the directory it came from.

    Convention-bound files such as changelogs and files matching an exclude
    pattern are skipped even when named explicitly.
    """
    files, skipped = [], []
    for arg in paths:
        p = Path(os.path.abspath(arg))
        if p.is_dir():
            candidates, base = markdown_files(p), p
        elif p.is_file():
            candidates, base = [p], None
        else:
            raise FileNotFoundError(arg)
        for f in candidates:
            rel = f.relative_to(base).as_posix() if base else arg
            if CONVENTION_FILES.match(f.name) or any(
                    fnmatch.fnmatch(rel, pattern) or fnmatch.fnmatch(f.name, pattern)
                    for pattern in excludes):
                skipped.append(display(f))
            else:
                files.append((f, base))
    return files, skipped


def markdown_files(folder: Path) -> list[Path]:
    """List Markdown files under a folder, honoring .gitignore inside a Git repository.

    Hidden folders are skipped, and symbolic links to other trees, such as
    linked repositories, are not followed.
    """
    listed = None
    if find_root(folder / '_') is not None:
        result = subprocess.run(['git', '-C', str(folder), 'ls-files', '--cached', '--others',
                                 '--exclude-standard', '-z', '--', '.'],
                                capture_output=True, text=True)
        if result.returncode == 0:
            listed = {folder / rel for rel in result.stdout.split('\0') if rel}
    found = []
    for current, dirs, names in os.walk(folder):
        dirs[:] = sorted(d for d in dirs if not d.startswith('.') and d != 'node_modules'
                         and not os.path.islink(os.path.join(current, d)))
        for name in sorted(names):
            path = Path(current) / name
            if name.lower().endswith('.md') and (listed is None or path in listed):
                found.append(path)
    return found


def display(path: Path) -> str:
    """Show paths below the working directory relatively, others in full."""
    try:
        rel = os.path.relpath(path)
    except ValueError:
        return str(path)
    return str(path) if rel.startswith('..') else rel


def sort_key(registry: dict, d: Diagnostic):
    entry = registry[d.code]
    order = list(registry).index(d.code)
    return GROUP_ORDER[entry['group']], SEVERITY_ORDER[entry['severity']], order, d.path, d.line


def render_text(registry: dict, fixes: dict[str, str], diagnostics: list[Diagnostic], outlines: dict[str, list[str]],
                checked: int, skipped: list[str]) -> str:
    out = []
    counts = {s: sum(registry[d.code]['severity'] == s for d in diagnostics) for s in SEVERITY_ORDER}
    if diagnostics:
        summary = f'{counts["error"]} error(s), {counts["warning"]} warning(s)'
        if counts['info']:
            summary += f', {counts["info"]} info'
        out.append(f'mddt: {summary} in {checked} file(s)')
    else:
        out.append(f'mddt: no problems in {checked} file(s)')
    if skipped:
        out.append(f'skipped convention files: {", ".join(skipped)}')
    current = None
    for d in sorted(diagnostics, key=lambda d: sort_key(registry, d)):
        if d.code != current:
            if current is not None:
                out.extend(fix_lines(fixes, current))
            current = d.code
            entry = registry[d.code]
            out.append('')
            out.append(f'{entry["severity"]} {d.code}: {entry["summary"]}')
            out.append(f'  rule: {SKILL_DIR / "references" / entry["rule"]}')
        out.append(f'  {d.path}:{d.line}  {d.detail}')
    if current is not None:
        out.extend(fix_lines(fixes, current))
    for lines in outlines.values():
        out.append('')
        out.append('outline ' + lines[0])
        out.extend('  ' + line for line in lines[1:])
    return '\n'.join(out) + '\n'


def fix_lines(fixes: dict[str, str], code: str) -> list[str]:
    text = fixes.get(code, '(no fix guidance)').strip()
    return ['  fix:'] + ['    ' + line if line else '' for line in text.splitlines()]


def render_json(registry: dict, diagnostics: list[Diagnostic], outlines: dict[str, list[str]],
                checked: list[str], skipped: list[str]) -> str:
    data = {
        'files': checked,
        'skipped': skipped,
        'diagnostics': [
            {
                'file': d.path,
                'line': d.line,
                'endLine': d.end_line,
                'code': d.code,
                'severity': registry[d.code]['severity'],
                'message': f'{registry[d.code]["summary"]}: {d.detail}',
            }
            for d in sorted(diagnostics, key=lambda d: sort_key(registry, d))
        ],
    }
    if outlines:
        data['outlines'] = outlines
    return json.dumps(data, ensure_ascii=False, indent=2) + '\n'


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog='mddt',
        description='Check Markdown files against the mddt document-tree model.')
    ap.add_argument('paths', nargs='+', help='Markdown files or directories to check')
    ap.add_argument('--outline', action='store_true',
                    help='print how each file was interpreted, even without structural findings')
    ap.add_argument('--review', action='store_true',
                    help='also report information for reviewing structure, and print every outline')
    ap.add_argument('--format', choices=('text', 'json'), default='text')
    ap.add_argument('--exclude', action='append', default=[], metavar='GLOB',
                    help='skip files matching GLOB, such as templates or fixtures; repeatable')
    ap.add_argument('--root', metavar='DIR',
                    help='top of the document tree; defaults to the Git repository root, '
                         'then to a directory argument')
    args = ap.parse_args(argv)

    registry = load_registry()
    try:
        files, skipped = collect(args.paths, args.exclude)
    except FileNotFoundError as missing:
        print(f'mddt: no such file or directory: {missing}', file=sys.stderr)
        return 2

    diagnostics: list[Diagnostic] = []
    outlines: dict[str, list[str]] = {}
    tree = Tree()
    fixed_root = Path(os.path.abspath(args.root)) if args.root else None
    for f, base in files:
        try:
            text = f.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError) as exc:
            print(f'mddt: cannot read {f}: {exc}', file=sys.stderr)
            return 2
        check = FileCheck(display(f), text)
        found = check.run()
        tree.check(f, check, fixed_root or find_root(f) or base)
        # Information supports deliberate structural review and stays hidden otherwise.
        found = [d for d in check.diagnostics
                 if args.review or registry[d.code]['severity'] != 'info']
        diagnostics.extend(found)
        structural = any(registry[d.code]['group'] == 'structure' for d in found)
        if args.outline or args.review or (structural and args.format == 'text'):
            outlines[check.path] = check.outline()

    if args.format == 'json':
        sys.stdout.write(render_json(registry, diagnostics, outlines,
                                     [display(f) for f, _ in files], skipped))
    else:
        sys.stdout.write(render_text(registry, load_fixes(), diagnostics, outlines,
                                     len(files), skipped))
    return 1 if any(registry[d.code]['severity'] == 'error' for d in diagnostics) else 0


if __name__ == '__main__':
    sys.exit(main())
