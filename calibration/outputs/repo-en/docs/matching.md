# How matching works

This document explains how pixtwin decides that photos are duplicates: exact matching, near-duplicate matching, special handling of bursts and rotation, and the metadata it reads.
The options mentioned here are listed in [configuration](configuration.md#options).

## Exact and near-duplicates

Exact duplicates are found by SHA-256.
Near-duplicates are found with a 64-bit difference hash (dHash), and two photos match when the Hamming distance between their hashes is at most `threshold`.

## Burst shots

Burst shots are photos from the same camera taken within 2 seconds of each other.
pixtwin compares them with `burst_threshold` instead of `threshold`.
A lower `burst_threshold` stops different shots of a burst from being grouped together.

## Rotated copies

When `detect_rotation = true`, pixtwin also hashes the 90, 180, and 270 degree rotations of each photo, so rotated copies match.
This adds about 30% to scan time.

## What is read from metadata

The EXIF orientation is applied before hashing, so a photo and its rotated-by-metadata copy match exactly.
EXIF data is also read for camera model, capture time (for burst detection), and rating.
Nothing else is stored.
