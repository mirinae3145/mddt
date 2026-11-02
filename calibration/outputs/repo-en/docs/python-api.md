# Python API

This document is the reference for pixtwin's Python API, the `Library` class.
The API is stable from 2.0 on and follows semantic versioning; anything not listed here is internal.

The `Library` class has these members:

| Member | What it does |
| --- | --- |
| `Library(index_path)` | Opens the index at `index_path` |
| `Library.scan(paths)` | Scans the given paths |
| `Library.groups(only=None)` | Returns the duplicate groups, optionally limited to one kind of match |
| `Library.plan(prefer=[])` | Returns the moves without performing them |
