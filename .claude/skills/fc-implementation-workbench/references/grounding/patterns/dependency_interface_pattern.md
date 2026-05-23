# Dependency Interface Pattern

## Baseline

Dependency interfaces in this codebase are typically:

- callout-shaped
- platform-semantic
- often multi-core aware
- frequently split between signal access, timing helpers, and bus helpers

Strong evidence:

- `Gp_TLE92104`
- `Gp_DRV8889`
- `IoMcu` family

## Rules

- Model dependency interfaces at FC/platform semantic level.
- Use `CalloutGetCoreId` when the target module truly follows per-core config/runtime access.
- Do not narrate raw bus transactions as if they were formal dependency interfaces unless the real FC exposes them that way.
