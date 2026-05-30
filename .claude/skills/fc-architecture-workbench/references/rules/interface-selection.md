# Interface Selection

Use this reference when deciding whether an FC dependency should be expressed as:
- a standard interface binding
- a macro replacement
- a callout
- fixed integration code with compile-time selection

## Overall Principle

Do not let existing platform APIs dictate the FC interface shape too early.

Start from the FC functional need:
- what does the FC need to do
- what information does the FC truly need to provide or obtain
- what result or status does the FC need back

Then choose the narrowest interface style that still preserves portability and integration flexibility.

## FC External Interfaces

Use function-based external interfaces by default.

Typical categories:
- `Init`
- `MainFunction`
- `Get...`
- `Set...`
- feature-specific control or query APIs

If the FC detects, latches, classifies, or reports faults/diagnostic states, include a readable external status interface by default. The naming depends on the AUTOSAR layer:

- `GetDevFaultSig` — IoExtDev chip-level fault diagnosis (external chip drivers)
- `GetXxxSigDiag` / `GetDiag` — IoMcu signal-level diagnostic (MCU peripheral drivers)
- project-equivalent fault/status query API

Do not hide fault visibility only inside internal flags when the requirement expects software-observable diagnosis.

Do not use global variables as FC external interfaces.

## Selection Rules

### Macro Replacement

Choose macro replacement when all of the following are true:
- dependency is very simple
- no complex parameter set is needed
- no special type conversion is needed
- no per-instance or per-channel scaling complexity is needed

Good examples:
- enter critical section
- leave critical section
- simple on or off hook with no identity mapping

Avoid when the dependency needs IDs, pointers, buffers, or adaptation logic.

### Standard Interface Binding

Choose standard binding when:
- the platform already defines a standard function shape
- several candidate providers share the same signature
- only the bound function name changes across projects

Good examples:
- project-wide signal getter or setter interface families

Require compile-safe fallback if the bound function is absent.

### Callout

Choose callout when one or more of the following are true:
- dependency meaning is project-specific
- hardware adaptation is needed
- board logic such as inversion or translation is needed
- parameters should reflect FC intent rather than platform implementation
- multiple IDs or scaling factors are needed

Good examples:
- set desired logical pin level while hiding DIO inversion details
- trigger SPI transfer with buffer and length while hiding AUTOSAR sequence details
- perform PWM output with instance-aware adaptation

Callout design rules:
- parameter names should reflect FC function intent
- put board-specific mapping or inversion logic inside callout code
- inspect downstream return values when meaningful
- return simple completion or status information back to FC if needed
- do not use array declarators in callout parameters; use pointer form such as `uint16* TxData_pu16`
- use `uint16 Size_u16` for data transfer size/count parameters by default
- for 16-bit SPI frame devices, use `uint16*` buffers instead of `uint8*` buffers to avoid repeated casts at call sites
- for byte-oriented I2C payloads, use `uint8*` buffers but still avoid `[]` syntax in prototypes

Recommended communication callout shapes:

- `Std_ReturnType <FC>_CalloutSpiTransceive(uint16 Id_u16, uint16* TxData_pu16, uint16* RxData_pu16, uint16 Size_u16)` for 16-bit SPI frame devices.
- `Std_ReturnType <FC>_CalloutI2cWrite(uint16 Id_u16, uint8* Data_pu8, uint16 Size_u16)` for byte-oriented I2C writes.
- `Std_ReturnType <FC>_CalloutI2cRead(uint16 Id_u16, uint8* Data_pu8, uint16 Size_u16)` for byte-oriented I2C reads.
- `Std_ReturnType <FC>_CalloutDioWrite(uint16 Id_u16, uint8 Level_u8)` for GPIO output control.
- `Std_ReturnType <FC>_CalloutDioRead(uint16 Id_u16, uint8* Level_pu8)` for GPIO input reading.
- `Std_ReturnType <FC>_CalloutPwmSetDuty(uint16 Id_u16, uint16 Duty_u16)` for PWM duty control.
- `Std_ReturnType <FC>_CalloutAdcRead(uint16 Id_u16, uint16* Value_pu16)` for ADC sampling (current/voltage sensing).
- `uint8 <FC>_CalloutGetCoreId(void)` for multi-core core identification.
- `void <FC>_CalloutDelayUs(uint32 Delay_us)` for microsecond-level timing delays.

### Fixed Integration Code

Choose fixed integration code with compile-time selection when:
- dependency options are few
- supported variants are stable
- efficiency matters more than flexibility
- the team can maintain the compile-time matrix safely

Good examples:
- a small set of known MCAL variants

If used, include an undefined or empty-safe option to avoid build breakage when the dependency is absent.

## Unification Guidance

Try to unify interfaces when:
- several dependencies share the same real semantic contract
- only provider names differ
- platform already has a stable standard pattern

Do not force unification when:
- semantics differ meaningfully
- one provider needs adaptation and another does not
- unification would leak platform-specific concepts into the FC

## Output Expectation

The final architecture artifact should explain:
- which dependencies were unified
- which were not unified
- which require callout
- why the chosen style is the best fit for the requirement
