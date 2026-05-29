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
- When interface execution steps or state-machine transitions contain delay/wait/timing requirements, generate a corresponding delay Callout (e.g. `CalloutDelayUs`, `CalloutWaitMs`). Do not leave timing dependencies implicit.
- Do not narrate raw bus transactions as if they were formal dependency interfaces unless the real FC exposes them that way.

## Recognized Callout Categories

| Category | When to Generate | Grounding Evidence |
|---|---|---|
| Core Identification | Multi-core with per-core routing | `Gp_TLE92104` |
| Delay / Timing | Wait, settling, debounce, or periodic timing requirements | `Gp_TLE92104` delay helpers |
| Bus Communication | SPI, I2C, or other bus access | `Gp_TLE92104`, `Gp_DRV8889` |
| Signal I/O | DIO, PWM, or other signal-level access | `Gp_TLE92104`, `IoMcu` |
| Platform Services | OS timestamps, critical sections, etc. | `IoMcu` |
