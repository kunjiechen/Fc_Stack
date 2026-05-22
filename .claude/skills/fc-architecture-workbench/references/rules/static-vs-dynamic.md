# Static vs Dynamic Classification

Use this reference when the requirement is ambiguous about whether an item belongs to configuration, calibration, runtime state, or dependency definition.

## Main Rule

Classify each extracted item using this priority:
1. Is it external capability rather than FC-owned data.
2. If it is FC-owned data, does it change during runtime.
3. If it does not change during runtime, is it truly calibratable.
4. If not calibratable, treat it as static configuration.

## Classification Summary

### Static Configuration

Use when the item is:
- determined before runtime
- stable during runtime
- project-specific or integration-specific
- used to shape behavior, mapping, feature coverage, or fixed limits

Typical examples:
- feature enable switches
- instance count
- channel or pin mapping
- timeout constants
- threshold constants without calibration flow
- OS or platform selection
- dependency binding mode

Default landing:
- `FC_Cfg.h`
- `FC_Cfg.c`
- `FC_CfgData.h`

### Dynamic Data

Use when the item is:
- updated each cycle or on events
- used as runtime cache, state, result, status, counter, or flag
- derived from current inputs or ongoing logic

Typical examples:
- sampled input values
- command outputs waiting for mainfunction processing
- last-cycle results
- state machine state
- retry counters
- debounce counters
- fault flags
- DET information

Default landing:
- internal variables in `FC.c`
- local variables in internal functions
- grouped state structures when appropriate

### Calibration Parameters

Use when the item is:
- intended to be adjustable after code design
- tied to calibration workflow or calibration tools
- not ordinary project configuration

Typical examples:
- tunable control gains
- field-adjusted thresholds
- algorithm behavior tuning constants

Use with caution for BSW FCs. Many embedded driver-level values that look like thresholds are still better treated as configuration.

Default landing:
- `FC_Cali.c`
- declaration visibility through `FC_CfgData.h` if needed by the project convention

### External Dependencies

Use when the item is:
- not FC-owned state or parameter
- an external service, peripheral access path, or another FC capability
- required for FC operation but implemented elsewhere

Typical examples:
- DIO write
- PWM output
- SPI transfer
- ADC read
- OS critical section service
- scheduler trigger
- core ID query

## Borderline Cases

### Threshold value

Ask:
- does it change during runtime
- does the project expect calibration tooling for it
- is it only a compile-time project constant

Decision:
- calibratable threshold with real tuning flow -> `Cali`
- fixed project threshold -> `Cfg`
- computed threshold used at runtime -> dynamic state

### Logical level inversion

This is usually not FC runtime data and not a visible FC parameter. Treat it as dependency adaptation logic, typically inside callout or integration code.

### Channel number or sequence ID

This is usually static configuration or dependency adaptation detail, not runtime state.

### Fault record

This is runtime state, usually internal dynamic data.

### User input written into FC and later processed by mainfunction

This is dynamic data even if it enters through a setter API.

## Output Expectation

When ambiguity exists, the generated architecture must state:
- selected classification
- short reason
- why nearby alternative classifications were not chosen

Use a table in the final output to make the decision auditable.
