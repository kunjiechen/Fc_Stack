# Architecture Release Workflow

Use this file when deciding architecture version progression, draft/release state, risk review handling, and release gating.

## Metadata

Architecture documents must carry:

- `Architecture Version: V1 / V2 / V3 / ...`
- `Architecture Status: Draft / Released`
- `Generation Time: concrete timestamp`

Use integer major versions only. Do not use `V1.0`, `V1.1`, or patch/minor versions.

## Version Strategy

- Requirement document only: generate initial architecture as `V1`.
- Initial architecture with unresolved items: mark `V1 Draft`.
- Draft architecture input with optional requirement document: update the draft and keep the same version.
- Draft architecture with all real risk items reviewed and no remaining modifications: promote to `Vx Released` without changing version.
- Released architecture plus requirement document: upgrade to next major version, such as `V1 -> V2`.

## Input Classification

- Treat architecture as `Released` only when metadata or body text clearly says `Released`, `正式发布`, or equivalent.
- Treat architecture as `Draft` when metadata says `Draft` / `草稿`, when any real risk item remains `待评审` or `待修改`, or when release evidence is missing.
- When both requirement and architecture are provided, compare the requirement against the architecture and summarize upgrade impact.
- When only a draft architecture is provided, focus on resolving pending confirmations and risks instead of creating a new version.

## Risk Review Contract

- Every risk row must have a stable index such as `R1`, `R2`, `R3`, and `R-OTHER`.
- Supported `状态` values are exactly `待评审`, `已评审`, and `待修改`.
- Use `备注` as the user-editable explanation column.
- If the user edits the Markdown table directly, treat `状态` and `备注` as the source of truth.
- If the user replies in chat, parse indexed decisions such as `R1、R3 已评审；R4 待修改，备注：采用回调通知`.
- If a row is `已评审`, do not change the architecture for that row unless the remark explicitly requests a change.
- If a row is `待修改` and `备注` is empty, execute the row's recommended action.
- If a row is `待修改` and `备注` is present, follow the remark first.

## Quick Draft Contract

`Quick Draft` is allowed only for draft outputs and only to reduce first-round review cost.

Rules:

- Keep architecture status as `Draft`.
- Keep a compact risk table with the top `3..5` highest-value real rows plus optional `R-OTHER`.
- Do not pretend a `Quick Draft` risk table is exhaustive.
- Before release review or formal handoff, expand the document to `Formal Draft`.
- Do not mark a `Quick Draft` architecture as `Released`.

## Release Gate

- Do not mark an architecture as `Released` while any real risk item remains `待评审` or `待修改`.
- Convert modified rows to `已评审` only after the requested change is fully incorporated.
- `R-OTHER` may be `已评审` with a remark such as `无其他建议`; otherwise it blocks release like any other real row.

## Post-Generation Guidance

When the generated or updated architecture remains `Draft`, the workflow guidance should always mention:

- edit the Markdown risk table directly by changing `状态` and `备注`
- reply in chat using risk indexes
- fastest release path: `全部已评审，R-OTHER 无其他建议，直接发布`
- modification path: mark rows as `待修改`; empty `备注` means use recommended action, otherwise follow the remark

## Change Summary

Every architecture update or upgrade should include a concise change summary covering meaningful deltas only:

- external interfaces
- dependency interfaces
- configuration, calibration, runtime-state, or MemMap changes
- file structure or include-relationship changes
- risks closed, risks added, or pending confirmations changed
- release status changes
