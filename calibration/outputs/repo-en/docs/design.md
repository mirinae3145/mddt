# Design

This document explains how pixtwin is built: its five-stage pipeline, the index, how groups are found, and why every move can be undone.
The behavior that results is described in [how matching works](matching.md) and in the [command reference](cli.md).

## Pipeline

The pipeline has five stages: scan, hash, group, plan, and move.
A rescan reuses the index from the earlier stages, so unchanged files are not hashed again.

## Index

The index is a SQLite database with tables for files, hashes, groups, and moves.
All profiles and all scanned roots share it.

## Grouping

Grouping uses a BK-tree over the hashes.
A BK-tree finds the hashes within a Hamming distance of a given hash without comparing it with every other hash.

## Move journal

Every move is written to a journal before it is carried out.
The journal is what makes `pixtwin undo` possible, including after a permission error stops a move partway.
