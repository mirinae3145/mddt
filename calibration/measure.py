# SPDX-FileCopyrightText: 2026 Taeha Shin
# SPDX-License-Identifier: MIT
# /// script
# requires-python = ">=3.11"
# dependencies = ["markdown-it-py>=3", "mdit-py-plugins>=0.4"]
# ///
"""Measure structural distributions of documents written for calibration.

Usage: uv run calibration/measure.py calibration/outputs

Each subfolder of the given folder is one document set; the report gives
percentiles per set and per language suffix (-en, -ko), using the checker's
own parsing so that the numbers match what its codes measure.
"""
import json, sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'skills/mddt/scripts'))
import mddt

OUT = Path(sys.argv[1])
LIST_TYPES = mddt.LIST_TYPES
data = defaultdict(lambda: defaultdict(list))  # metric -> cell -> values


def add(metric, cell, value):
    data[metric][cell].append(value)


for cell_dir in sorted(p for p in OUT.iterdir() if p.is_dir()):
    cell = cell_dir.name
    for f in sorted(cell_dir.rglob('*.md')):
        check = mddt.FileCheck(str(f), f.read_text(encoding='utf-8'))
        add('file_lines', cell, check.line_count)
        for node in check.root.walk():
            if node.type == 'paragraph' and node.map and not mddt.is_badge_paragraph(node):
                sents = check.sentences(node)
                add('paragraph_sentences', cell, len(sents))
                for _, words in sents:
                    add('sentence_words', cell, words)
        run = 0
        for block in check.blocks + [None]:
            if block is not None and block.type in mddt.TRANSPARENT:
                continue
            if block is not None and block.type == 'paragraph':
                run += 1
                continue
            if run:
                add('paragraph_run', cell, run)
            run = 0
        groups = defaultdict(list)
        for k, h in enumerate(check.headings):
            owner = next((j for j in range(k - 1, -1, -1) if check.headings[j].level < h.level), -1)
            groups[(owner, h.level)].append(k)
        for (owner, level), sib in groups.items():
            if level > 1:
                add('sibling_headings', cell, len(sib))
            if len(sib) < 2:
                continue
            sizes = {k: check.section_lines(k) for k in sib}
            for k, size in sizes.items():
                others = sorted(v for j, v in sizes.items() if j != k)
                add('sibling_ratio', cell, round(size / max(others[len(others) // 2], 1), 2))

        def walk(node, depth):
            items = [c for c in node.children if c.type == 'list_item']
            add('list_items', cell, len(items))
            add('list_depth', cell, depth)
            for item in items:
                named = mddt.name_of(item)
                if named:
                    add('name_words', cell, len(named[1].split()))
                if node.type != 'ordered_list':
                    n = sum(len(check.sentences(c)) for c in item.children if c.type == 'paragraph')
                    add('item_sentences', cell, n)
                for c in item.children:
                    if c.type in LIST_TYPES:
                        walk(c, depth + 1)
        for block in check.blocks:
            if block.type in LIST_TYPES:
                walk(block, 1)


def pct(values, p):
    v = sorted(values)
    return v[min(len(v) - 1, int(round(p / 100 * (len(v) - 1))))]


def summary(values):
    return {'n': len(values), 'p50': pct(values, 50), 'p90': pct(values, 90), 'p95': pct(values, 95), 'max': max(values)}


report = {}
for metric, cells in data.items():
    row = {}
    for cell, values in cells.items():
        row[cell] = summary(values)
    for group, keys in (('en', [c for c in cells if c.endswith('-en')]), ('ko', [c for c in cells if c.endswith('-ko')]),
                        ('all', list(cells))):
        values = [v for c in keys for v in cells[c]]
        if values:
            row[group] = summary(values)
    report[metric] = row
print(json.dumps(report, ensure_ascii=False, indent=1))
