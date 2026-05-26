# FC Detailed-Design Workflow

## Goal

Move from prompt-heavy document generation to a repeatable workflow:

1. grounding selection
2. structured input assembly
3. architecture and DD model generation
4. markdown rendering
5. automatic validation

## Workflow

### 1. Freeze grounding baseline

- Use `references/grounding/grounding_scope.md`
- Choose the most relevant grounding modules from `references/grounding/index.yaml`

### 2. Build structured input

- Read source requirement inputs
- Convert them into the schema family under `references/schemas/`
- Normalize field usage with `references/schemas/field_dictionary.md`
- Record each downgrade, freeze, or pending confirmation explicitly
- Use `scripts/build_generation_bundle.py` when source artifacts already exist as markdown and need to be converted into a reusable bundle skeleton
- When source `Cfg.c` exists, use `scripts/extract_cfg_objects.py` or the `--source-root` option on `build_generation_bundle.py` to attach real config objects instead of only requirement-side config points

### 3. Generate grounding summary

Before writing architecture or detailed design, produce a short summary answering:

- which grounding modules were used
- which patterns were adopted
- which patterns were rejected
- why

When the source artifacts already exist, `build_generation_bundle.py` may infer a first-pass `grounding_patterns` and `grounding_rejections` set from formal interfaces, config items, and `Conf_*` evidence. Review and tighten those values before final publishing.

### 4. Generate architecture and DD models

- freeze external interfaces from architecture
- freeze dependency interfaces from architecture
- derive internal interfaces from repeated responsibilities
- attach relationship links explicitly
- attach grounding evidence and `Conf_*` evidence where they influenced the design

For detailed-design narrative generation, also use:

- `references/detailed_design_quality_contract.md`
- `references/bundle_to_dd_mapping.md`
- `references/chapter_generation_rules.md`

### 5. Render markdown

- render architecture markdown
- render detailed design markdown
- keep source-of-truth in structured models instead of markdown text only

### 6. Run validators

Current validator:

- `scripts/validate_fc_docs.py`
- `scripts/validate_generation_bundle.py`
- `scripts/run_regression_pack.py`

Current checks:

- generation bundle schema validation
- grounding module legality against `grounding/index.yaml`
- top-level and nested module consistency
- architecture formal interface coverage in detailed design bundle
- SRS to architecture external-interface consistency when SRS is supplied
- SRS to detailed-design external-interface consistency when SRS is supplied
- external interface consistency
- dependency interface consistency
- `关联接口` presence in DD interface tables
- explicit conditional-interface detection
- undefined local relationship-reference detection

## Immediate Next Work

- harden structured model generation helpers with more module samples
- extend regression cases beyond the current `Gp_NCA95yy` baseline to `Gp_TLE92104` and `Gp_DRV8889`
