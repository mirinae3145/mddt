# Contributing to pixtwin

This document tells contributors how pixtwin's source is organized, which checks a change must pass, what a pull request needs, and how maintainers make releases.
For what the tool does, see the [README](README.md).

## Source layout

The source is in `src/pixtwin`, with one module per concern:

- **`cli`**: The command-line entry points.
- **`scan`**: Walking the library and reading files.
- **`hashing`**: Computing the hashes.
- **`grouping`**: Building duplicate groups from hashes.
- **`planning`**: Deciding which photo is kept and what moves.
- **`index`**: The SQLite index.

The modules follow the stages described in [design](docs/design.md).

## Checks

CI enforces all three of the following checks on every pull request.
Run them locally before you push.

- **Tests**: `pytest -q`
- **Linting**: `ruff`
- **Type checking**: `mypy`

CI runs the test suite on Python 3.10 to 3.13 on Linux, macOS, and Windows.

## Test fixtures

Test fixtures are small synthetic images in `tests/photos`.
Never add personal photos.

## Pull requests

Every pull request includes tests and a changelog entry.
Open an issue before proposing a new feature.

## Releases

Maintainers make releases; contributors do not.
Releases are tagged `vMAJOR.MINOR.PATCH` on the main branch.

1. Write the changelog entry for the release.
1. Push the release tag.
1. CI builds the wheel and uploads it to PyPI and to the releases page.

The changelog entry comes first because pushing the tag starts the upload.
