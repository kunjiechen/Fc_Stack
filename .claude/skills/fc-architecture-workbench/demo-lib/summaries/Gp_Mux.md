# Gp_Mux FC Architecture Summary

This summary replaces the retained demo source/config files for future FC architecture work. Use it as style evidence, not as a mandatory implementation template.

## Positioning

- Layer: IoExtDev external device layer
- Role: Select mux channels, sample DIO/ADC values through dependencies, and expose logical-level/ADC signal reads by ID.
- Best-fit scenario: Multiplexer / channel-selection FC; good reference for mapping-heavy multi-channel designs and periodic switching/cache pattern.

## External Interfaces

| Interface Prototype | Architecture Meaning | Notes |
| --- | --- | --- |
| `void Gp_Mux_Init(void)` | Initialization/lifecycle. | Keep semantic API naming and full parameter validity checks where applicable. |
| `void Gp_Mux_MainFunction(void)` | Periodic/background processing. | Keep semantic API naming and full parameter validity checks where applicable. |
| `Std_ReturnType Gp_Mux_GetLvlSig(uint16 Id_u16, boolean* DioLvl_pb)` | Runtime external API. | Keep semantic API naming and full parameter validity checks where applicable. |
| `Std_ReturnType Gp_Mux_GetAdcSig(uint16 Id_u16, uint16* AdcRaw_pu16)` | Runtime external API. | Keep semantic API naming and full parameter validity checks where applicable. |

## Dependency Interfaces / Callouts

| Interface Prototype | Dependency Meaning | Implementation Boundary |
| --- | --- | --- |
| `uint32 Gp_Mux_CalloutGetCoreId(void)` | Hardware/platform action outside FC ownership. | Project Adaptation / MCAL / resource layer as appropriate. |
| `void Gp_Mux_CalloutReadDioChannel(uint16 ChannelId_u16, boolean* ChannelLvl_pb)` | Hardware/platform action outside FC ownership. | DIO/IoMcu or project adaptation. |
| `void Gp_Mux_CalloutWriteDioChannel(uint16 ChannelId_u16, uint8 Level_u8)` | Hardware/platform action outside FC ownership. | DIO/IoMcu or project adaptation. |
| `void Gp_Mux_CalloutGetAdcRaw(uint16 Id_u16, uint16* AdcRaw_pu16)` | Hardware/platform action outside FC ownership. | ADC/IoMcu or signal service adaptation. |

## Configuration and Calibration Guidance

- Per-core enable and multi-chip count are count/size macros.
- Chip/channel/signal mapping belongs in configuration data.
- No per-interface enable macros are needed for GetLvlSig/GetAdcSig unless project trim is explicit.

## Runtime-State Guidance

- Per-chip runtime stores selected channel, cached DIO/ADC value, and sequencing state.
- MainFunction advances channel switching and refreshes cached values; external getters return cached values.

## MemMap Guidance

- CODE for API and switching helpers.
- CONST per-core config sections for chip and signal mapping.
- CLEAR_FAR_DATA per-core runtime data.

## Reusable Architecture Lessons

- For mux-like FCs, keep external APIs logical and minimal; mapping complexity belongs in config tables.
- Use periodic refresh when hardware sequencing cannot be completed synchronously inside getters.

## Use and Non-Use Rules

- Use this summary to select architecture patterns, not to copy all interfaces or macros blindly.
- Re-run configuration macro necessity checks before promoting any macro to formal output.
- Re-run dependency necessity checks before promoting any callout to formal output.
- Prefer user requirements and current project constraints over this historical sample summary.
