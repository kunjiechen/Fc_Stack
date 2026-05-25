# Raw Extraction Policy

## 1. Purpose

This file defines how raw requirement input should be extracted before formal requirement construction.

Its job is not to decide final SRS wording. Its job is to:

- split raw input into stable items
- remove metadata noise
- preserve source references
- normalize obvious fields
- prepare items for formal requirement gate classification

## 2. Two-Layer Model

Raw extraction must be treated as two layers.

### Layer A: Structure Extraction

Responsible for:

- line splitting
- heading and metadata detection
- spreadsheet field extraction
- source reference preservation
- basic category hints

This layer answers:

- what raw item exists
- where it came from
- what fields it contains

It must not assume every extracted item is already a formal requirement.

### Layer B: Semantic Disposition

Responsible for deciding whether the extracted item belongs to:

- `formal_requirement`
- `constraint`
- `capability`
- `metadata`
- `evidence`
- `architecture_seed_only`
- `test_seed_only`
- `open_issue`

This layer answers:

- should the item enter the formal requirement pool
- should it stay as constraint/evidence only
- should it feed only architecture/test seed

## 3. Noise Filtering Rules

The following should normally be filtered before the formal requirement gate:

- module name
- module abbreviation
- document number
- chapter titles such as `原始功能需求`
- pure section labels without software behavior

These may remain in module identity or source inventory but should not become formal requirements.

## 4. Input Preference

When structured spreadsheet fields exist, prefer field meaning over free-text heuristics.

When only plain text exists, use heuristics conservatively and preserve uncertainty.

## 5. Output Requirement

Every raw extracted item should retain:

- source reference
- category hint
- normalized description
- disposition
- gate reason

Without those, later bundle validation cannot explain why an item entered or did not enter the formal pool.
