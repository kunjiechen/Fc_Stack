

{0}------------------------------------------------

# 16-bit I<sup>2</sup>C-bus I/O port with interrupt and reset

Datasheet (EN) 1.0

## Product Overview

The NCA9539-Q1 is a 24-pin device that provides 16 bits of General Purpose parallel Input/Output (GPIO) expansion for the two-line bidirectional I<sup>2</sup>C bus applications. The device can operate with a power supply voltage (V<sub>DD</sub>) range from 1.65 V to 3.6 V. It provides a simple solution when additional I/Os are needed for ACPI power switches, sensors, push buttons, LEDs, fans, etc.

The NCA9539-Q1 consists of two 8-bit Configuration (Input or Output selection); Input, Output and Polarity Inversion (active HIGH or active LOW operation) registers. The system master can enable the I/Os as either inputs or outputs by writing to the I/O configuration bits. The data for each Input or Output is kept in the corresponding Input or Output register. The polarity of the read register can be inverted with the Polarity Inversion register. All registers can be read by the system master.

The NCA9539-Q1 open-drain interrupt output is activated when any input state differs from its corresponding input port register state and is used to indicate to the system master that an input state has changed. The power-on reset sets the registers to their default values and initializes the device state machine. Also, the NCA9539-Q1 has a hardware RESET pin that can be used to reset the device to its default state.

The hardware pins (A0, A1) vary the fixed I<sup>2</sup>C-bus address and allow up to four devices to share the same I<sup>2</sup>C-bus.

## Key Features

- AEC-Q100 (Grade 1): Qualified for automotive applications
- I<sup>2</sup>C to Parallel Port Expander
- Operating power supply voltage range of 1.65 V to 3.6 V
- Low standby current
- Open-drain active-low interrupt output
- Active-low reset input
- 5 V tolerant, 16 I/O ports which default to input mode
- Compatible with most microcontrollers
- Up to 400 kHz Fast I<sup>2</sup>C bus
- Noise filter on SCL/SDA inputs
- Polarity Inversion register
- Internal power-on reset
- No glitch on power-up
- Address by two hardware address pins for use of up to four devices
- Latched outputs with high-current drive capability for directly driving LEDs
- Latch-up performance exceeds 100 mA per JESD 78, class II
- ESD protection exceeds JESD 22: 2000 V HBM, 200 V MM, and 1000 V CDM

## Applications

- Automotive infotainment, ADAS, automotive body electronics, HEV, EV and powertrain
- Industrial automation, factory automation
- GPIO expansion for I<sup>2</sup>C-bus applications
- Servers, personal computers, personal electronics
- Routers (telecom switching equipment)
- Products with GPIO-Limited processors

## Device Information

| Part Number    | Package | Body Size     |
|----------------|---------|---------------|
| NCA9539-Q1TSXR | TSSOP24 | 7.80mm*4.40mm |

## Functional Block Diagrams

![Functional Block Diagram of NCA9539-Q1 showing pin connections. The diagram shows a 24-pin package with pins 1-12 on the left and 24-13 on the right. Pins 1-12 include INT, A1, RESET, P00-P07, and VSS. Pins 24-13 include VDD, SDA, SCL, A0, P17-P10. The central component is labeled NCA9539-Q1.](4d4c0d9569f139f1b68b2c2549c9a299_img.jpg)

Functional Block Diagram of NCA9539-Q1 showing pin connections. The diagram shows a 24-pin package with pins 1-12 on the left and 24-13 on the right. Pins 1-12 include INT, A1, RESET, P00-P07, and VSS. Pins 24-13 include VDD, SDA, SCL, A0, P17-P10. The central component is labeled NCA9539-Q1.

Figure 1. NCA9539-Q1 Block Diagram

{1}------------------------------------------------

## INDEX

|                                                              |           |
|--------------------------------------------------------------|-----------|
| <b>1. PIN CONFIGURATION AND FUNCTIONS</b> .....              | <b>3</b>  |
| <b>2. ABSOLUTE MAXIMUM RATINGS</b> .....                     | <b>4</b>  |
| <b>3. RECOMMENDED OPERATING CONDITIONS</b> .....             | <b>4</b>  |
| <b>4. THERMAL CHARACTERISTICS</b> .....                      | <b>5</b>  |
| <b>5. SPECIFICATIONS</b> .....                               | <b>5</b>  |
| <b>5.1. ELECTRICAL CHARACTERISTICS</b> .....                 | <b>5</b>  |
| <b>5.2. DYNAMIC CHARACTERISTICS</b> .....                    | <b>7</b>  |
| <b>5.3. PARAMETER MEASUREMENT INFORMATION</b> .....          | <b>9</b>  |
| <b>6. DETAILED DESCRIPTION</b> .....                         | <b>11</b> |
| <b>6.1. FUNCTIONAL BLOCK DIAGRAM</b> .....                   | <b>11</b> |
| <b>6.2. FEATURE DESCRIPTION</b> .....                        | <b>12</b> |
| 6.2.1. I/O port .....                                        | 12        |
| 6.2.2. RESET\ input .....                                    | 12        |
| 6.2.3. Interrupt (INT\ ) Output .....                        | 13        |
| <b>6.3. DEVICE FUNCTIONAL MODES</b> .....                    | <b>13</b> |
| 6.3.1. Power-On Reset .....                                  | 13        |
| <b>6.4. PROGRAMMING</b> .....                                | <b>13</b> |
| 6.4.1. I2C Interface .....                                   | 13        |
| 6.4.2. Start and Stop Conditions .....                       | 14        |
| 6.4.3. Bit Transfer .....                                    | 14        |
| 6.4.4. System Configuration .....                            | 15        |
| 6.4.5. Acknowledge .....                                     | 15        |
| <b>6.5. REGISTER MAPS</b> .....                              | <b>16</b> |
| 6.5.1. Device Address .....                                  | 16        |
| 6.5.2. Control Register and Command Byte .....               | 16        |
| 6.5.3. Registers 0 and 1: Input port register pair .....     | 17        |
| 6.5.4. Registers 2 and 3: Output port registers .....        | 17        |
| 6.5.5. Registers 4 and 5: Polarity inversion registers ..... | 18        |
| 6.5.6. Registers 6 and 7: Configuration registers .....      | 18        |
| <b>6.6. BUS TRANSACTIONS</b> .....                           | <b>19</b> |
| 6.6.1. Writing to the Port Registers .....                   | 19        |
| 6.6.2. Reading the Port Registers .....                      | 19        |
| <b>7. APPLICATION DESIGN-IN INFORMATION</b> .....            | <b>22</b> |
| <b>7.1. APPLICATION INFORMATION</b> .....                    | <b>22</b> |
| <b>7.2. TYPICAL APPLICATION</b> .....                        | <b>22</b> |
| <b>8. ORDER INFORMATION</b> .....                            | <b>22</b> |
| <b>9. DOCUMENTATION SUPPORT</b> .....                        | <b>23</b> |
| <b>10. PACKAGE INFORMATION</b> .....                         | <b>24</b> |
| <b>11. TAPE AND REEL INFORMATION</b> .....                   | <b>24</b> |
| <b>12. REVISION HISTORY</b> .....                            | <b>25</b> |

{2}------------------------------------------------

# 1. Pin Configuration and Functions

![Diagram of the NCA9539-Q1 package showing pin configuration. The package is a 24-pin integrated circuit. Pins are numbered 1 to 24. Pins 1-12 are on the left side, and pins 13-24 are on the right side. The pin numbers are listed next to their respective pins. The central part of the package is labeled NCA9539-Q1. A small circle is located in the top-left corner of the package, indicating the orientation.](69edc2887e907309499ac95b47ab6905_img.jpg)

Diagram of the NCA9539-Q1 package showing pin configuration. The package is a 24-pin integrated circuit. Pins are numbered 1 to 24. Pins 1-12 are on the left side, and pins 13-24 are on the right side. The pin numbers are listed next to their respective pins. The central part of the package is labeled NCA9539-Q1. A small circle is located in the top-left corner of the package, indicating the orientation.

Figure 1-1. NCA9539-Q1 Package

Table 1-1. NCA9539-Q1 Pin Configuration and Description

| SYMBOL | PIN NO. | Function                                                               |
|--------|---------|------------------------------------------------------------------------|
| INT\   | 1       | Interrupt open-drain output. Connect to VDD through a pull-up resistor |
| A1     | 2       | Address input 1. Connect directly to VDD or ground                     |
| RESET\ | 3       | Active-low reset input. Connect to VDD through a pull-up resistor      |
| P00    | 4       | Port 0 input/output. At power-on, the port is configured as an input   |
| P01    | 5       | Port 0 input/output. At power-on, the port is configured as an input   |
| P02    | 6       | Port 0 input/output. At power-on, the port is configured as an input   |
| P03    | 7       | Port 0 input/output. At power-on, the port is configured as an input   |
| P04    | 8       | Port 0 input/output. At power-on, the port is configured as an input   |
| P05    | 9       | Port 0 input/output. At power-on, the port is configured as an input   |
| P06    | 10      | Port 0 input/output. At power-on, the port is configured as an input   |
| P07    | 11      | Port 0 input/output. At power-on, the port is configured as an input   |
| VSS    | 12      | Ground                                                                 |
| P10    | 13      | Port 1 input/output. At power-on, the port is configured as an input   |
| P11    | 14      | Port 1 input/output. At power-on, the port is configured as an input   |

{3}------------------------------------------------

| SYMBOL | PIN NO. | Function                                                             |
| ------ | ------- | -------------------------------------------------------------------- |
| P12    | 15      | Port 1 input/output. At power-on, the port is configured as an input |
| P13    | 16      | Port 1 input/output. At power-on, the port is configured as an input |
| P14    | 17      | Port 1 input/output. At power-on, the port is configured as an input |
| P15    | 18      | Port 1 input/output. At power-on, the port is configured as an input |
| P16    | 19      | Port 1 input/output. At power-on, the port is configured as an input |
| P17    | 20      | Port 1 input/output. At power-on, the port is configured as an input |
| A0     | 21      | Address input 0. Connect directly to VDD or ground                   |
| SCL    | 22      | Serial clock bus. Connect to VDD through a pull-up resistor          |
| SDA    | 23      | Serial data bus. Connect to VDD through a pull-up resistor           |
| VDD    | 24      | Supply voltage                                                       |

# 2. Absolute Maximum Ratings

| Parameters                     | Symbol              | Min  | Typ | Max | Unit | Comments |
|--------------------------------|---------------------|------|-----|-----|------|----------|
| Supply voltage                 | V <sub>DD</sub>     | -0.5 |     | 3.6 | V    |          |
| Voltage on an input/output pin | V <sub>I/O</sub>    | -0.5 |     | 6.0 | V    |          |
| Output current                 | I <sub>O</sub>      | -    |     | ±50 | mA   |          |
| Input current                  | I <sub>I</sub>      | -    |     | ±20 | mA   |          |
| Supply current                 | I <sub>DD</sub>     | -    |     | 160 | mA   |          |
| Ground supply current          | I <sub>SS</sub>     | -    |     | 200 | mA   |          |
| Total power dissipation        | P <sub>tot</sub>    | -    |     | 200 | mW   |          |
| Maximum junction temperature   | T <sub>j(max)</sub> | -    |     | 135 | °C   |          |
| Storage temperature            | T <sub>stg</sub>    | -65  |     | 150 | °C   |          |
| Ambient temperature            | T <sub>amb</sub>    | -40  |     | 125 | °C   |          |

# 3. Recommended Operating Conditions

| Parameters               | Symbol          | Min                 | Typ | Max                 | Unit |
|--------------------------|-----------------|---------------------|-----|---------------------|------|
| Supply voltage           | V <sub>DD</sub> | 1.65                |     | 3.6                 | V    |
| High-level input voltage | V <sub>IH</sub> | 0.7*V <sub>DD</sub> |     | 3.6                 | V    |
| Low-level input voltage  | V <sub>IL</sub> | -0.5                |     | 0.3*V <sub>DD</sub> | V    |

{4}------------------------------------------------

| Parameters                          | Symbol   | Min | Typ | Max | Unit |
| ----------------------------------- | -------- | --- | --- | --- | ---- |
| High-level output current (IO port) | $I_{OH}$ |     |     | -10 | mA   |
| Low-level output current (IO port)  | $I_{OL}$ |     |     | 10  | mA   |
| Low-level output current (INT, SDA) | $I_{OL}$ |     |     | 3.5 | mA   |
| Operating free-air temperature      | $T_A$    | -40 |     | 125 | °C   |

# 4. Thermal Characteristics

| Parameters                                | Symbol               | TSSOP24 | Unit |
|-------------------------------------------|----------------------|---------|------|
| IC Junction-to-Air Thermal Resistance     | $R_{\theta JA}$      | 108.8   | °C/W |
| Junction-to-case (top) thermal resistance | $R_{\theta JC(top)}$ | 54      | °C/W |
| Junction-to-board thermal resistance      | $R_{\theta JB}$      | 62.8    | °C/W |

# 5. Specifications

## 5.1. Electrical Characteristics

$V_{DD} = 1.65V$  to  $3.6V$ ;  $T_{amb} = -40^\circ C$  to  $125^\circ C$ ; unless otherwise noted.

| Parameters                | Symbol    | Min  | Typ  | Max | Unit    | Conditions                                                                                               |
|---------------------------|-----------|------|------|-----|---------|----------------------------------------------------------------------------------------------------------|
| Input diode clamp voltage | $V_{IK}$  | -1.2 | -    | -   | V       | $I_I = -18mA$                                                                                            |
| <b>Supplies</b>           |           |      |      |     |         |                                                                                                          |
| Supply voltage Range      | $V_{DD}$  | 1.65 | -    | 3.6 | V       |                                                                                                          |
| Supply current            | $I_{DD}$  | -    | 12.5 | 30  | $\mu A$ | Operating mode; $V_{DD} = 3.6 V$ ; I/O=input; $V_I = V_{DD}$ ; no load; $f_{SCL} = 400 kHz$              |
|                           |           | -    | 7.5  | 19  | $\mu A$ | Operating mode; $V_{DD} = 2.7 V$ ; I/O=input; $V_I = V_{DD}$ ; no load; $f_{SCL} = 400 kHz$              |
|                           |           | -    | 4.4  | 11  | $\mu A$ | Operating mode; $V_{DD} = 1.95 V$ ; I/O=input; $V_I = V_{DD}$ ; no load; $f_{SCL} = 400 kHz$             |
|                           |           | -    | 3.5  | 9   | $\mu A$ | Operating mode; $V_{DD} = 1.65 V$ ; I/O=input; $V_I = V_{DD}$ ; no load; $f_{SCL} = 400 kHz$             |
| Standby current           | $I_{STB}$ | -    | 0.14 | 5   | $\mu A$ | Standby mode; $V_{DD} = 3.6 V$ ; I/O=input; $V_I = V_{DD}$ ; no load; $V_I = V_{SS}$ ; $f_{SCL} = 0 kHz$ |
|                           |           | -    | 0.08 | 4.5 | $\mu A$ | Standby mode; $V_{DD} = 2.7 V$ ; I/O=input; $V_I = V_{DD}$ ; no load; $V_I = V_{SS}$ ; $f_{SCL} = 0 kHz$ |

{5}------------------------------------------------

| Parameters                                     | Symbol     | Min                | Typ  | Max                | Unit | Conditions                                                                                                              |
| ---------------------------------------------- | ---------- | ------------------ | ---- | ------------------ | ---- | ----------------------------------------------------------------------------------------------------------------------- |
|                                                |            | -                  | 0.05 | 3.5                | μA   | Standby mode; $V_{DD} = 1.95 \text{ V}$ ; I/O=input; $V_I=V_{DD}$ ; no load; $V_I = V_{SS}$ ; $f_{SCL} = 0 \text{ kHz}$ |
|                                                |            | -                  | 0.04 | 2.5                | μA   | Standby mode; $V_{DD} = 1.65 \text{ V}$ ; I/O=input; $V_I=V_{DD}$ ; no load; $V_I = V_{SS}$ ; $f_{SCL} = 0 \text{ kHz}$ |
|                                                |            | -                  | 0.11 | 13                 | μA   | Standby mode; $V_{DD} = 3.6 \text{ V}$ ; I/O=input; $V_I=V_{SS}$ ; no load; $V_I = V_{SS}$ ; $f_{SCL} = 0 \text{ kHz}$  |
|                                                |            | -                  | 0.08 | 9.5                | μA   | Standby mode; $V_{DD} = 2.7 \text{ V}$ ; I/O=input; $V_I=V_{SS}$ ; no load; $V_I = V_{SS}$ ; $f_{SCL} = 0 \text{ kHz}$  |
|                                                |            | -                  | 0.05 | 6.5                | μA   | Standby mode; $V_{DD} = 1.95 \text{ V}$ ; I/O=input; $V_I=V_{SS}$ ; no load; $V_I = V_{SS}$ ; $f_{SCL} = 0 \text{ kHz}$ |
|                                                |            | -                  | 0.04 | 5.5                | μA   | Standby mode; $V_{DD} = 1.65 \text{ V}$ ; I/O=input; $V_I=V_{SS}$ ; no load; $V_I = V_{SS}$ ; $f_{SCL} = 0 \text{ kHz}$ |
| Power On Reset Voltage, Rising <sup>[1]</sup>  | $V_{PORR}$ | 0.75               | 1.17 | 1.5                | V    | no load; $V_I = V_{DD}$ or $V_{SS}$                                                                                     |
| Power On Reset Voltage, Falling <sup>[1]</sup> | $V_{PORF}$ | 0.75               | 1.05 | 1.5                | V    | no load; $V_I = V_{DD}$ or $V_{SS}$                                                                                     |
| <b>Input SCL; Input and Output SDA</b>         |            |                    |      |                    |      |                                                                                                                         |
| LOW-level input voltage                        | $V_{IL}$   | -0.5               | -    | $0.3 \cdot V_{DD}$ | V    |                                                                                                                         |
| HIGH-level input voltage                       | $V_{IH}$   | $0.7 \cdot V_{DD}$ | -    | 3.6                | V    |                                                                                                                         |
| LOW-level output current                       | $I_{OL}$   | 3                  | -    | -                  | mA   | $V_{DD} = 1.65 \text{ V}$ to $3.6 \text{ V}$ ; $V_{OL} = 0.4 \text{ V}$                                                 |
| Input leakage current                          | $I_L$      | -1                 | -    | 1                  | μA   | $V_{DD} = 1.65 \text{ V}$ to $3.6 \text{ V}$ ; $V_I = V_{DD}$ or $V_{SS}$                                               |
| Input capacitance                              | $C_i$      | -                  | 6    | 10                 | pF   | $V_I = V_{SS}$                                                                                                          |
| <b>I/Os</b>                                    |            |                    |      |                    |      |                                                                                                                         |
| LOW-level input voltage                        | $V_{IL}$   | -0.5               | -    | $0.3 \cdot V_{DD}$ | V    |                                                                                                                         |
| HIGH-level input voltage                       | $V_{IH}$   | $0.7 \cdot V_{DD}$ | -    | 3.6                | V    |                                                                                                                         |
| LOW-level output current                       | $I_{OL}$   | 8                  | -    | -                  | mA   | $V_{DD} = 1.65 \text{ V}$ to $3.6 \text{ V}$ ; $V_{OL} = 0.3 \text{ V}$ <sup>[2]</sup>                                  |
|                                                |            | 10                 | -    | -                  | mA   | $V_{DD} = 1.65 \text{ V}$ to $3.6 \text{ V}$ ; $V_{OL} = 0.35 \text{ V}$ <sup>[2]</sup>                                 |
| HIGH-level output voltage                      | $V_{OH}$   | 1.2                | -    | -                  | V    | $I_{OH} = -8 \text{ mA}$ ; $V_{DD} = 1.65 \text{ V}$ <sup>[3]</sup>                                                     |
|                                                |            | 1.0                | -    | -                  | V    | $I_{OH} = -10 \text{ mA}$ ; $V_{DD} = 1.65 \text{ V}$ <sup>[3]</sup>                                                    |

{6}------------------------------------------------

| Parameters                       | Symbol           | Min                 | Typ | Max                 | Unit | Conditions                                                                             |
| -------------------------------- | ---------------- | ------------------- | --- | ------------------- | ---- | -------------------------------------------------------------------------------------- |
|                                  |                  | 1.7                 | -   | -                   | V    | I <sub>OH</sub> = -8 mA; V <sub>DD</sub> = 2.3 V <sup>[3]</sup>                        |
|                                  |                  | 1.4                 | -   | -                   | V    | I <sub>OH</sub> = -10 mA; V <sub>DD</sub> = 2.3 V <sup>[3]</sup>                       |
|                                  |                  | 2.5                 | -   | -                   | V    | I <sub>OH</sub> = -8 mA; V <sub>DD</sub> = 3.0 V <sup>[3]</sup>                        |
|                                  |                  | 2.4                 | -   | -                   | V    | I <sub>OH</sub> = -10 mA; V <sub>DD</sub> = 3.0 V <sup>[3]</sup>                       |
|                                  |                  | 3.3                 | -   | -                   | V    | I <sub>OH</sub> = -8 mA; V <sub>DD</sub> = 3.6 V <sup>[3]</sup>                        |
|                                  |                  | 3.2                 | -   | -                   | V    | I <sub>OH</sub> = -10 mA; V <sub>DD</sub> = 3.6 V <sup>[3]</sup>                       |
| HIGH-level input leakage current | I <sub>LIH</sub> | -                   | -   | 1                   | μA   | V <sub>DD</sub> = 3.6 V; V <sub>I</sub> = V <sub>DD</sub>                              |
| LOW-level input leakage current  | I <sub>LIL</sub> | -                   | -   | -1                  | μA   | V <sub>DD</sub> = 3.6 V; V <sub>I</sub> = V <sub>SS</sub>                              |
| Input capacitance                | C <sub>i</sub>   | -                   | 3.7 | 9.5                 | pF   |                                                                                        |
| Output capacitance               | C <sub>o</sub>   | -                   | 3.7 | 9.5                 | pF   |                                                                                        |
| <b>Interrupt <i>INT</i></b>      |                  |                     |     |                     |      |                                                                                        |
| LOW-level output current         | I <sub>OL</sub>  | 3                   | -   | -                   | mA   | V <sub>DD</sub> = 1.65 V to 3.6 V; V <sub>OL</sub> = 0.4V                              |
| <b>Select Inputs A0, A1</b>      |                  |                     |     |                     |      |                                                                                        |
| LOW-level input voltage          | V <sub>IL</sub>  | -0.5                | -   | 0.3*V <sub>DD</sub> | V    |                                                                                        |
| HIGH-level input voltage         | V <sub>IH</sub>  | 0.7*V <sub>DD</sub> | -   | 3.6                 | V    |                                                                                        |
| Input leakage current            | I <sub>LI</sub>  | -1                  | -   | 1                   | μA   | V <sub>DD</sub> = 1.65 V to 3.6 V; V <sub>I</sub> = V <sub>DD</sub> or V <sub>SS</sub> |
| <b><i>RESET</i></b>              |                  |                     |     |                     |      |                                                                                        |
| Input leakage current            | I <sub>LI</sub>  | -1                  | -   | 1                   | μA   | V <sub>DD</sub> = 1.65 V to 3.6 V; RESET = V <sub>DD</sub> or V <sub>SS</sub>          |

1. V<sub>DD</sub> must be lowered to 0.2V for at least 50μs in order to reset part.
2. Each I/O must be externally limited to a maximum of 25 mA and each octal (P00 to P07 and P10 to P17) must be limited to a maximum current of 100 mA for a device total of 200 mA.
3. The total current sourced by all I/Os must be limited to 160 mA.

## 5.2. Dynamic Characteristics

V<sub>DD</sub> = 1.65V to 3.6V; T<sub>amb</sub> = -40°C to 125°C; unless otherwise noted.

| Parameters | Symbol | Standard-mode I2C-bus | Fast-mode I2C-bus | Unit |
|------------|--------|-----------------------|-------------------|------|
|------------|--------|-----------------------|-------------------|------|

{7}------------------------------------------------

|                                                                   |                         | Min | Max  | Min                 | Max |         |
|-------------------------------------------------------------------|-------------------------|-----|------|---------------------|-----|---------|
| SCL clock frequency                                               | $f_{SCL}$               | 0   | 100  | 0                   | 400 | kHz     |
| bus free time between a STOP and START condition                  | $t_{BUF}$               | 4.7 | -    | 1.3                 | -   | $\mu s$ |
| hold time (repeated) START condition                              | $t_{HD;STA}$            | 4.0 | -    | 0.6                 | -   | $\mu s$ |
| set-up time for a repeated START condition                        | $t_{SU;STA}$            | 4.7 | -    | 0.6                 | -   | $\mu s$ |
| set-up time for STOP condition                                    | $t_{SU;STO}$            | 4.0 | -    | 0.6                 | -   | $\mu s$ |
| data valid acknowledge time                                       | $t_{VD;ACK}^{[1]}$      | 0.3 | 3.45 | 0.1                 | 0.9 | $\mu s$ |
| data hold time                                                    | $t_{HD;DAT}$            | 0   | -    | 0                   | -   | ns      |
| data valid time                                                   | $t_{VD;DAT}^{[2]}$      | 300 | -    | 50                  | -   | ns      |
| data set-up time                                                  | $t_{SU;DAT}$            | 250 | -    | 100                 | -   | ns      |
| LOW period of the SCL clock                                       | $t_{LOW}$               | 4.7 | -    | 1.3                 | -   | $\mu s$ |
| HIGH period of the SCL clock                                      | $t_{HIGH}$              | 4.0 | -    | 0.6                 | -   | $\mu s$ |
| fall time of both SDA and SCL signals                             | $t_f$                   | -   | 300  | $20 + 0.1C_b^{[3]}$ | 300 | ns      |
| rise time of both SDA and SCL signals                             | $t_r$                   | -   | 1000 | $20 + 0.1C_b^{[3]}$ | 300 | ns      |
| pulse width of spikes that must be suppressed by the input filter | $t_{SP}$                | -   | 50   | -                   | 50  | ns      |
| reset pulse width                                                 | $t_{w(rst)}$            | 6   | -    | 6                   | -   | ns      |
| reset recovery time                                               | $t_{rec(rst)}$          | 200 | -    | 200                 | -   | ns      |
| reset time                                                        | $t_{rst}$               | 400 | -    | 400                 | -   | ns      |
| data output valid time                                            | $t_{v(Q)}$              | -   | 300  | -                   | 300 | ns      |
| data input set-up time                                            | $t_{su(D)}$             | 150 | -    | 150                 | -   | ns      |
| data input hold time                                              | $t_{h(D)}$              | 1   | -    | 1                   | -   | $\mu s$ |
| valid time on pin /INT                                            | $t_{v(INT\_N)}^{[4]}$   | -   | 4    | -                   | 4   | $\mu s$ |
| reset time on pin /INT                                            | $t_{rst(INT\_N)}^{[5]}$ | -   | 4    | -                   | 4   | $\mu s$ |

1.  $t_{VD;ACK}$  = time for acknowledgement signal from SCL LOW to SDA (out) LOW, see Figure 5-3.
2.  $t_{VD;DAT}$  = minimum time for SDA data out to be valid following SCL LOW, see Figure 5-3.
3.  $C_b$  = total capacitance of one bus line in pF.
4.  $t_{v(INT\_N)}$  is measured from 50% IO input to  $0.3 \cdot V_{DD}$  on INT\
5.  $t_{rst(INT\_N)}$  is measured from  $0.3 \cdot V_{DD}$  on SCL to  $0.7 \cdot V_{DD}$  on INT\.

{8}------------------------------------------------

## 5.3. Parameter Measurement Information

![Figure 5-1: Test circuitry for switching times. A block diagram showing a PULSE GENERATOR connected to an input pin <math>V_i</math>. The input pin has a termination resistor <math>R_T</math> to ground. The output of the pulse generator is connected to the input of a DUT (Device Under Test). The output of the DUT is connected to an output pin <math>V_o</math>. The output pin has a load capacitor <math>C_L</math> (50pF) to ground and a load resistor <math>R_L</math> (500Ω) connected to a switch. The switch can connect the load resistor to VDD, open, or GND.](b3baf3a29b67c7425d2562ddbc52f0cc_img.jpg)

Figure 5-1: Test circuitry for switching times. A block diagram showing a PULSE GENERATOR connected to an input pin  $V_i$ . The input pin has a termination resistor  $R_T$  to ground. The output of the pulse generator is connected to the input of a DUT (Device Under Test). The output of the DUT is connected to an output pin  $V_o$ . The output pin has a load capacitor  $C_L$  (50pF) to ground and a load resistor  $R_L$  (500Ω) connected to a switch. The switch can connect the load resistor to VDD, open, or GND.

$R_L$  = load resistor.

$C_L$  = load capacitance includes jig and probe capacitance.

$R_T$  = termination resistance should be equal to the output impedance of  $Z_o$  of the pulse generators.

Figure 5-1. Test circuitry for switching times

![Figure 5-2: Definition of timing on I2C-bus. A timing diagram showing SDA and SCL signals. The SDA signal has parameters <math>t_{BUF}</math>, <math>t_{LOW}</math>, <math>t_r</math>, <math>t_f</math>, <math>t_{HD;STA}</math>, <math>t_{SP}</math>, <math>t_{HD;DAT}</math>, <math>t_{HIGH}</math>, <math>t_{SU;DAT}</math>, <math>t_{SU;STA}</math>, and <math>t_{SU;STO}</math>. The SCL signal has parameters <math>t_{HD;STA}</math>, <math>t_{SU;STA}</math>, and <math>t_{SU;STO}</math>. The diagram also shows the 9th clock and the transition from a stop (Sr) to a start (P) condition. Voltage levels are indicated as 0.7 * VDD and 0.3 * VDD.](0d5fdb87a392819c7d2e3b6230912a0b_img.jpg)

Figure 5-2: Definition of timing on I2C-bus. A timing diagram showing SDA and SCL signals. The SDA signal has parameters  $t_{BUF}$ ,  $t_{LOW}$ ,  $t_r$ ,  $t_f$ ,  $t_{HD;STA}$ ,  $t_{SP}$ ,  $t_{HD;DAT}$ ,  $t_{HIGH}$ ,  $t_{SU;DAT}$ ,  $t_{SU;STA}$ , and  $t_{SU;STO}$ . The SCL signal has parameters  $t_{HD;STA}$ ,  $t_{SU;STA}$ , and  $t_{SU;STO}$ . The diagram also shows the 9th clock and the transition from a stop (Sr) to a start (P) condition. Voltage levels are indicated as 0.7 \* VDD and 0.3 \* VDD.

Figure 5-2. Definition of timing on I2C-bus

![Figure 5-3: Parameter Measurement Waveform: <math>t_{VD;DAT}</math> & <math>t_{VD;ACK}</math>. A timing diagram showing SCL and SDA signals. The SCL signal is a square wave with a 9th clock indicated. The SDA signal is a square wave. The time interval between the falling edge of the SCL signal and the falling edge of the SDA signal is labeled <math>t_{VD;DAT}</math>. The time interval between the falling edge of the SCL signal and the falling edge of the SDA signal (for the ACK signal) is labeled <math>t_{VD;ACK}</math>. Voltage levels are indicated as 0.7 * VDD and 0.3 * VDD.](4495fbec19aac6861f1a0b35c4dc38bc_img.jpg)

Figure 5-3: Parameter Measurement Waveform:  $t_{VD;DAT}$  &  $t_{VD;ACK}$ . A timing diagram showing SCL and SDA signals. The SCL signal is a square wave with a 9th clock indicated. The SDA signal is a square wave. The time interval between the falling edge of the SCL signal and the falling edge of the SDA signal is labeled  $t_{VD;DAT}$ . The time interval between the falling edge of the SCL signal and the falling edge of the SDA signal (for the ACK signal) is labeled  $t_{VD;ACK}$ . Voltage levels are indicated as 0.7 \* VDD and 0.3 \* VDD.

Figure 5-3. Parameter Measurement Waveform:  $t_{VD;DAT}$  &  $t_{VD;ACK}$

![Figure 5-4: P-port Load Configuration. A block diagram showing a pin labeled 'Pn' connected to a load. The load consists of a capacitor <math>C_L</math> (50pF) to ground and a resistor <math>R_L</math> (500Ω) connected to a switch. The switch can connect the resistor to 2*VDD, open, or GND.](2ba086df3506f81bae3a9b53725dcfea_img.jpg)

Figure 5-4: P-port Load Configuration. A block diagram showing a pin labeled 'Pn' connected to a load. The load consists of a capacitor  $C_L$  (50pF) to ground and a resistor  $R_L$  (500Ω) connected to a switch. The switch can connect the resistor to 2\*VDD, open, or GND.

Figure 5-4. P-port Load Configuration

{9}------------------------------------------------

![Timing diagram showing SCL and INT signals. SCL is a clock signal with 1st, 2nd, 8th, and 9th clock cycles indicated. INT is an interrupt signal that goes high after the 9th clock. t_rst(INT_N) is the time from the falling edge of the 9th clock to the rising edge of INT. Voltage levels are 0.7 * VDD and 0.3 * VDD.](7801d00a216dc4dc8a7d210dcb5fe3c5_img.jpg)

The figure is a timing diagram for parameter measurement. It shows two signals: SCL (Serial Clock) and INT (Interrupt). The SCL signal is a periodic clock waveform. The first, second, eighth, and ninth clock cycles are explicitly labeled. A dashed line indicates a gap between the second and eighth clocks. The INT signal is shown below the SCL signal. It is initially low and then transitions to high. The time interval  $t_{rst(INT\_N)}$  is measured from the falling edge of the ninth clock cycle on the SCL signal to the rising edge of the INT signal. Voltage levels for both signals are indicated as  $0.7 * V_{DD}$  for the high level and  $0.3 * V_{DD}$  for the low level.

Timing diagram showing SCL and INT signals. SCL is a clock signal with 1st, 2nd, 8th, and 9th clock cycles indicated. INT is an interrupt signal that goes high after the 9th clock. t\_rst(INT\_N) is the time from the falling edge of the 9th clock to the rising edge of INT. Voltage levels are 0.7 \* VDD and 0.3 \* VDD.

Figure 5-5. Parameter Measurement Waveform:  $t_{rst(INT\_N)}$

{10}------------------------------------------------

# 6. Detailed Description

## 6.1. Functional Block Diagram

![Functional block diagram of NCA9539-Q1 showing internal components like I2C-BUS CONTROL, SHIFT REGISTER, I/O PORT, INPUT FILTER, POWER-ON RESET, and INTERRUPT LOGIC with their respective connections to pins A0, A1, SCL, SDA, RESET, VDD, VSS, P00~P07, P10~P17, and INT.](d26959f4514c26ca19c3d6f00da85956_img.jpg)

The block diagram illustrates the internal architecture of the NCA9539-Q1. The main components are:

- I<sup>2</sup>C-BUS CONTROL**: Receives address lines A0 and A1. It is connected to an **INPUT FILTER** for the SCL and SDA pins. The SDA pin is an open-drain output with an internal pull-down transistor. This block also receives 'Write pulse' and 'Read pulse' signals from the I/O PORT.
- SHIFT REGISTER**: A 16-bit register that interfaces bidirectionally with the I<sup>2</sup>C-BUS CONTROL and the I/O PORT.
- I/O PORT**: Consists of two 8-bit ports, P00 ~ P07 and P10 ~ P17. It receives 16-bit data from the SHIFT REGISTER and generates 'Write pulse' and 'Read pulse' signals for the I<sup>2</sup>C-BUS CONTROL.
- POWER-ON RESET**: Takes RESET\, VDD, and VSS as inputs and provides a reset signal to the I<sup>2</sup>C-BUS CONTROL and INTERRUPT LOGIC.
- INTERRUPT LOGIC**: Receives signals from the I/O PORT and passes them through an LP FILTER to the INT pin. The INT pin is pulled up to VDD by an external resistor.

Functional block diagram of NCA9539-Q1 showing internal components like I2C-BUS CONTROL, SHIFT REGISTER, I/O PORT, INPUT FILTER, POWER-ON RESET, and INTERRUPT LOGIC with their respective connections to pins A0, A1, SCL, SDA, RESET, VDD, VSS, P00~P07, P10~P17, and INT.

Figure 6-1. Block Diagram of NCA9539-Q1

{11}------------------------------------------------

![Simplified schematic of I/Os for the NCA9539-Q1. The diagram shows the internal logic and transistors for an I/O pin. It includes a Configuration Register (D FF), two Shift Registers (D FF), an Output Port Register (D FF), an Input Port Register (D FF), and a Polarity Inversion Register (D FF). Transistors Q1 and Q2 are used to drive the I/O pin, with an ESD Protection Diode. Logic gates (AND, OR, XOR) are used to generate control signals for the registers and the I/O pin. The I/O pin is connected to VDD and VSS through the transistors and diode.](042733dc5e8e7f5f30b60adba3266cde_img.jpg)

The schematic illustrates the internal architecture of the I/O pins. On the left, several flip-flops (FF) are shown:
 

- A **Configuration Register** (D FF) receives 'Data from Shift Register' and 'Write Configuration Pulse'. Its Q output is connected to one input of an AND gate.
- An **Output Port Register** (D FF) receives 'Data from Shift Register' and 'Write Pulse'. Its Q output is connected to the other input of the same AND gate.
- The AND gate's output drives the gate of an N-channel MOSFET labeled **Q1**. Q1's source is connected to **VDD** and its drain is connected to the **I/O pin**.
- Another flip-flop (D FF) receives 'Data from Shift Register' and 'Read Pulse'. Its Q output is connected to one input of an OR gate.
- The OR gate's output drives the gate of an N-channel MOSFET labeled **Q2**. Q2's source is connected to **VSS** and its drain is connected to the **I/O pin**.
- An **Input Port Register** (D FF) receives data from the I/O pin and is clocked by 'Read Pulse'. Its Q output is connected to one input of an XOR gate.
- A **Polarity Inversion Register** (D FF) receives 'Data from Shift Register' and 'Write Polarity Pulse'. Its Q output is connected to the other input of the XOR gate.
- The XOR gate's output is labeled **Input Port Register Data** and is also connected to **To INT**.
- Another XOR gate takes the output of the first XOR gate and the Q output of the Polarity Inversion Register as inputs. Its output is labeled **Polarity Inversion Register Data**.
- An **ESD Protection Diode** is connected between the I/O pin and VSS.

Simplified schematic of I/Os for the NCA9539-Q1. The diagram shows the internal logic and transistors for an I/O pin. It includes a Configuration Register (D FF), two Shift Registers (D FF), an Output Port Register (D FF), an Input Port Register (D FF), and a Polarity Inversion Register (D FF). Transistors Q1 and Q2 are used to drive the I/O pin, with an ESD Protection Diode. Logic gates (AND, OR, XOR) are used to generate control signals for the registers and the I/O pin. The I/O pin is connected to VDD and VSS through the transistors and diode.

Figure 6-2. Simplified schematic of I/Os

## 6.2. Feature description

#### 6.2.1. I/O port

When an I/O is configured as an input, FETs Q1 and Q2 are off, creating a high-impedance input. The input voltage may be raised above  $V_{DD}$  to a maximum of 3.6V.

If the I/O is configured as an output, then either Q1 or Q2 is on, depending on the state of the Output Port register. Care should be exercised if an external voltage is applied to an I/O configured as an output because of the low-impedance path that exists between the pin and either  $V_{DD}$  or  $V_{SS}$ .

#### 6.2.2. RESET\ input

A reset can be accomplished by holding the RESET\ pin low for a minimum of  $t_w$ . The NCA9539-Q1 registers and I2C state machine are held in their default states until RESET\ is once again high. This input requires a pull-up resistor to  $V_{DD}$ , if no active connection is used.

{12}------------------------------------------------

![Timing diagram for RESET\ signal relative to SCL, SDA, and Port signals. The diagram shows the relationship between the SCL signal (with START and ACK or read cycle markers), the SDA signal (with 30% threshold markers), the RESET\ signal (with 50% threshold markers and timing parameters t_rec(tst), t_w(rst), and t_rst), and the Port signal. The RESET\ signal is shown transitioning from a high state to a low state and then back to a high state. The t_rec(tst) parameter is the time from the rising edge of the SCL signal to the rising edge of the RESET\ signal. The t_w(rst) parameter is the pulse width of the reset signal. The t_rst parameter is the time from the falling edge of the RESET\ signal to the rising edge of the RESET\ signal.](b05a8a3551db31147979064952179990_img.jpg)

Timing diagram for RESET\ signal relative to SCL, SDA, and Port signals. The diagram shows the relationship between the SCL signal (with START and ACK or read cycle markers), the SDA signal (with 30% threshold markers), the RESET\ signal (with 50% threshold markers and timing parameters t\_rec(tst), t\_w(rst), and t\_rst), and the Port signal. The RESET\ signal is shown transitioning from a high state to a low state and then back to a high state. The t\_rec(tst) parameter is the time from the rising edge of the SCL signal to the rising edge of the RESET\ signal. The t\_w(rst) parameter is the pulse width of the reset signal. The t\_rst parameter is the time from the falling edge of the RESET\ signal to the rising edge of the RESET\ signal.

Figure 6-3. Definition of RESET\ timing

#### 6.2.3. Interrupt (INT\) Output

An interrupt is activated at any rising or falling edge of the port inputs changing state in the input mode. After time,  $t_{iv}$ , the signal INT\ is valid. The interrupt is deactivated when data on the port is changed to the original setting or data is read from the port that generated the interrupt. Resetting occurs in the read mode at the acknowledge (ACK) bit after the rising edge of the SCL signal. Each change of the I/Os after resetting is detected and is transmitted as INT\.

Since each 8-bit port is read independently, the interrupt caused by port 0 is not cleared by a read of port 1, or vice versa. Reading from or writing to another device does not affect the interrupt circuit, and a pin configured as an output cannot cause an interrupt. Changing an I/O from an output to an input may cause a false interrupt to occur if the state of the pin does not match the contents of the Input Port register.

INT\ has an open-drain structure and requires a pull-up resistor to VDD.

## 6.3. Device functional modes

#### 6.3.1. Power-On Reset

When power is applied to VDD, an internal power-on reset holds the NCA9539-Q1 in a reset condition until VDD has reached  $V_{POR}$ . At that point, the reset condition is released and the NCA9539-Q1 registers and I2C state machine will initialize to their default states. The power-on reset typically completes the reset and enables the part by the time the power supply is above  $V_{POR}$ . However, when it is required to reset the part by lowering the power supply, it is necessary to lower it below 0.2 V for at least 50 $\mu$ s.

## 6.4. Programming

#### 6.4.1. I2C Interface

The NCA9539-Q1 has a standard bidirectional I2C interface that is controlled by a master device in order to be configured or read the status of this device.

The I2C-bus is for 2-way, 2-line communication between different ICs or modules. The two lines are a serial data line (SDA) and a serial clock line (SCL). Both lines must be connected to a positive supply via a pull-up resistor when connected to the output stages of a device. The size of the pull-up resistor is determined by the amount of capacitance on the I2C lines. Data transfer may be initiated only when the bus is idle.

{13}------------------------------------------------

Each slave on the I2C bus has a specific device address to differentiate between other slave devices that are on the same I2C bus. Many slave devices require configuration upon startup to set the behavior of the device. This is typically done when the master accesses internal register maps of the slave, which have unique register addresses. A device can have one or multiple registers where data is stored, written, or read.

The general procedure for a master to access a slave device is as below.

1. If a master wants to send data to a slave:

- Master-transmitter sends a START condition and addresses the slave-receiver.
- Master-transmitter sends data to slave-receiver.
- Master-transmitter terminates the transfer with a STOP condition.

2. If a master wants to receive or read data from a slave:

- Master-receiver sends a START condition and addresses the slave-transmitter.
- Master-receiver sends the requested register to read to slave-transmitter.
- Master-receiver receives data from the slave-transmitter.
- Master-receiver terminates the transfer with a STOP condition.

Note: MSB first in data transfer.

#### 6.4.2. Start and Stop Conditions

A HIGH-to-LOW transition of the data line while the clock is HIGH is defined as the START condition (S). A LOW-to-HIGH transition of the data line while the clock is HIGH is defined as the STOP condition (P). A bus is considered idle if both SDA and SCL lines are high after a STOP condition.

![Timing diagram showing START and STOP conditions on SDA and SCL lines.](35bae65e940db581c7559355e04dbb76_img.jpg)

The diagram illustrates the timing for START (S) and STOP (P) conditions on an I2C bus. The top line represents the SDA (Serial Data) signal, and the bottom line represents the SCL (Serial Clock) signal. The diagram is divided into three sections by vertical dashed lines: 'START condition', 'Data transfer', and 'STOP condition'. In the 'START condition' section, the SDA line transitions from HIGH to LOW while the SCL line is HIGH. In the 'Data transfer' section, both SDA and SCL lines show square wave signals. In the 'STOP condition' section, the SDA line transitions from LOW to HIGH while the SCL line is HIGH.

Timing diagram showing START and STOP conditions on SDA and SCL lines.

Figure 6-4. Definition of START and STOP conditions

#### 6.4.3. Bit Transfer

One data bit is transferred during each clock pulse. The data on the SDA line must remain stable during the HIGH period of the clock pulse as changes in the data line at this time will be interpreted as control signals.

{14}------------------------------------------------

![Timing diagram for I2C bit transfer showing SDA and SCL signals. The SDA line is shown with a transition from high to low, and the SCL line is shown with a transition from low to high. The diagram indicates that the data line is stable and valid during the high period of the clock line, and that the data can only change when the clock line is low.](177e8bc1c595b7fe3461d9919f87e044_img.jpg)

The diagram shows two waveforms: SDA (top) and SCL (bottom). The SCL waveform is a periodic square wave. The SDA waveform is a piecewise constant line that changes its state only when the SCL line is low. Vertical dashed lines divide the timeline into clock periods. In the first clock period, the SDA line is high while the SCL line is high, then the SCL line goes low, and the SDA line changes to low. In the second clock period, the SDA line remains low while the SCL line goes high and then low again. Labels indicate 'Data line stable; Data valid' during the high period of the SCL clock and 'Change of data allowed' during the low period of the SCL clock.

Timing diagram for I2C bit transfer showing SDA and SCL signals. The SDA line is shown with a transition from high to low, and the SCL line is shown with a transition from low to high. The diagram indicates that the data line is stable and valid during the high period of the clock line, and that the data can only change when the clock line is low.

Figure 6-5. Bit transfer

#### 6.4.4. System Configuration

A device generating a message is a 'transmitter'; a device receiving is the 'receiver'. The device that controls the message is the 'master' and the devices which are controlled by the master are the 'slaves' (see Figure 6-6).

![System configuration diagram showing multiple masters and slaves connected to a common I2C bus. The bus consists of two lines: SCL and SDA. The SCL line is connected to the SCL pins of all devices. The SDA line is connected to the SDA pins of all devices. The devices are labeled: MASTER TRANSMITTER/RECEIVER, SLAVE RECEIVER, SLAVE TRANSMITTER/RECEIVER, MASTER TRANSMITTER, MASTER TRANSMITTER/RECEIVER, and I2C-BUS MULTIPLEXER. The I2C-BUS MULTIPLEXER is connected to a SLAVE device.](9ae17964ddd9b814c7d905b1af2fddf2_img.jpg)

The diagram illustrates a system configuration on an I2C bus. Two horizontal lines represent the bus: the top line is SCL and the bottom line is SDA. Several devices are connected to these lines: a 'MASTER TRANSMITTER/RECEIVER', a 'SLAVE RECEIVER', a 'SLAVE TRANSMITTER/RECEIVER', a 'MASTER TRANSMITTER', and another 'MASTER TRANSMITTER/RECEIVER'. An 'I<sup>2</sup>C-BUS MULTIPLEXER' is also connected to the bus and has a 'SLAVE' device connected to it. All devices are connected to both the SCL and SDA lines, forming a common bus network.

System configuration diagram showing multiple masters and slaves connected to a common I2C bus. The bus consists of two lines: SCL and SDA. The SCL line is connected to the SCL pins of all devices. The SDA line is connected to the SDA pins of all devices. The devices are labeled: MASTER TRANSMITTER/RECEIVER, SLAVE RECEIVER, SLAVE TRANSMITTER/RECEIVER, MASTER TRANSMITTER, MASTER TRANSMITTER/RECEIVER, and I2C-BUS MULTIPLEXER. The I2C-BUS MULTIPLEXER is connected to a SLAVE device.

Figure 6-6. System configuration

#### 6.4.5. Acknowledge

The number of data bytes transferred between the START and the STOP conditions from transmitter to receiver is not limited. Each byte of eight bits is followed by one acknowledge bit. The acknowledge bit is a HIGH level put on the bus by the transmitter, whereas the master generates an extra acknowledge related clock pulse.

A slave receiver which is addressed must generate an acknowledge after the reception of each byte. In the same way, a master must generate an acknowledge after the reception of each byte that has been clocked out of the slave transmitter. The device that acknowledges must pull down the SDA line during the acknowledge clock pulse, so that the SDA line is stable LOW during the HIGH period of the acknowledge related clock pulse; set-up time and hold time must be taken into account.

A master receiver must signal an end of data to the transmitter by not generating an acknowledge on the last byte that has been clocked out of the slave. In this event, the transmitter must leave the data line HIGH to enable the master to generate a STOP condition.

{15}------------------------------------------------

![Timing diagram showing Data output by transmitter, Data output by receiver, and SCL from master over time. It illustrates the START condition, clock pulses, and acknowledgement signals.](b3df5964338063224492c01f09e4fed6_img.jpg)

The diagram shows three horizontal lines representing signals over time. The top line, 'Data output by transmitter', starts with a high-to-low transition labeled 'START condition' (S). It then shows several data segments. The middle line, 'Data output by receiver', shows a 'Not acknowledge' signal (high) and an 'acknowledge' signal (low) following a clock pulse. The bottom line, 'SCL from master', shows a series of clock pulses labeled 1, 2, ..., 8, 9. A 'Clock pulse for acknowledgement' is indicated at pulse 9.

Timing diagram showing Data output by transmitter, Data output by receiver, and SCL from master over time. It illustrates the START condition, clock pulses, and acknowledgement signals.

Figure 6-7. Acknowledgement on I<sup>2</sup>C-bus

### 6.5. Register Maps

The register maps of the NCA9539-Q1 include input port registers, output port registers, polarity inversion port registers and configuration registers.

#### 6.5.1. Device Address

Figure 6-8 shows the address byte of the NCA9539-Q1. The last bit of the target address defines the operation (read or write) to be performed. A HIGH (1) selects a read operation, while a LOW (0) selects a write operation.

![Diagram of Slave Address byte structure showing Fixed bits (11101) and Programmable bits (A1 A0 R/W).](b90144cfbb81a2d610d920240fda689d_img.jpg)

The diagram shows an 8-bit byte structure for 'Slave Address'. The first five bits are '1 1 1 0 1', grouped by a bracket labeled 'Fixed'. The next two bits are 'A1 A0', grouped by a bracket labeled 'Programmable'. The last bit is 'R/W', also part of the 'Programmable' group.

Diagram of Slave Address byte structure showing Fixed bits (11101) and Programmable bits (A1 A0 R/W).

Figure 6-8. NCA9539-Q1 device address

Table 6-1 shows the address reference of the NCA9539-Q1.

Table 6-1. Address Reference

| Inputs | Inputs | I <sup>2</sup> C Bus Slave Address |
| ------ | ------ | ---------------------------------- |
| A1     | A0     |                                    |
| L      | L      | 116(decimal), 74h(hexadecimal)     |
| L      | H      | 117(decimal), 75h(hexadecimal)     |
| H      | L      | 118(decimal), 76h(hexadecimal)     |
| H      | H      | 119(decimal), 77h(hexadecimal)     |

#### 6.5.2. Control Register and Command Byte

Following the successful acknowledgment of the address byte, the bus controller sends a command byte shown in Table 6-2 that is stored in the write-only control register in the NCA9539-Q1. Three bits of this data byte state the operation (read or write) and the internal register (input, output, Polarity Inversion or Configuration) that is affected. The command byte is sent only during a write transmission. Figure 6-9 shows the control register bits.

{16}------------------------------------------------

| 0   | 0   | 0   | 0   | 0   | B2  | B1  | B0  |
| --- | --- | --- | --- | --- | --- | --- | --- |

Figure 6-9. NCA9539-Q1 control register bits

Table 6-2. Command byte

| Control Register Bits | Control Register Bits | Control Register Bits | Command Byte Hex | Register                  | Protocol        | Power-up Default |
| --------------------- | --------------------- | --------------------- | ---------------- | ------------------------- | --------------- | ---------------- |
| B2                    | B1                    | B0                    |                  |                           |                 |                  |
| 0                     | 0                     | 0                     | 00h              | Input port 0              | Read byte       | 1111 1111        |
| 0                     | 0                     | 1                     | 01h              | Input port 1              | Read byte       | 1111 1111        |
| 0                     | 1                     | 0                     | 02h              | Output port 0             | Read/write byte | 1111 1111        |
| 0                     | 1                     | 1                     | 03h              | Output port 1             | Read/write byte | 1111 1111        |
| 1                     | 0                     | 0                     | 04h              | Polarity inversion port 0 | Read/write byte | 0000 0000        |
| 1                     | 0                     | 1                     | 05h              | Polarity inversion port 1 | Read/write byte | 0000 0000        |
| 1                     | 1                     | 0                     | 06h              | Configuration port 0      | Read/write byte | 1111 1111        |
| 1                     | 1                     | 1                     | 07h              | Configuration port 1      | Read/write byte | 1111 1111        |

#### 6.5.3. Registers 0 and 1: Input port register pair

This register pair is an input-only port. It reflects the incoming logic levels of the pins, regardless of whether the pin is defined as an input or an output by Registers 6 and 7. Writing to this register pair has no effect.

Table 6-3. Input Port 0 Register

| Bit     | 7    | 6    | 5    | 4    | 3    | 2    | 1    | 0    |
|---------|------|------|------|------|------|------|------|------|
| Symbol  | I0.7 | I0.6 | I0.5 | I0.4 | I0.3 | I0.2 | I0.1 | I0.0 |
| Default | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 1    |

Table 6-4. Input Port 1 Register

| Bit     | 7    | 6    | 5    | 4    | 3    | 2    | 1    | 0    |
|---------|------|------|------|------|------|------|------|------|
| Symbol  | I1.7 | I1.6 | I1.5 | I1.4 | I1.3 | I1.2 | I1.1 | I1.0 |
| Default | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 1    |

#### 6.5.4. Registers 2 and 3: Output port registers

This register pair is an output-only port. It reflects the outgoing logic levels of the pins defined as outputs by Registers 6 and 7. Bit values in this register pair have no effect on pins defined as inputs. In turn, reading from this register reflects the value that is in the flip-flop controlling the output selection, not the actual pin value.

{17}------------------------------------------------

Table 6-5. Output Port 0 Register

| Bit     | 7    | 6    | 5    | 4    | 3    | 2    | 1    | 0    |
|---------|------|------|------|------|------|------|------|------|
| Symbol  | O0.7 | O0.6 | O0.5 | O0.4 | O0.3 | O0.2 | O0.1 | O0.0 |
| Default | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 1    |

Table 6-6. Output Port 1 Register

| Bit     | 7    | 6    | 5    | 4    | 3    | 2    | 1    | 0    |
|---------|------|------|------|------|------|------|------|------|
| Symbol  | O1.7 | O1.6 | O1.5 | O1.4 | O1.3 | O1.2 | O1.1 | O1.0 |
| Default | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 1    |

#### 6.5.5. Registers 4 and 5: Polarity inversion registers

This register pair allows the user to invert the polarity of the Input port register data. If a bit in this register is set (written with 1), the corresponding input port pin's polarity is inverted. If a bit in this register is cleared (written with 0), the corresponding input port pin's original polarity is retained.

Table 6-7. Polarity Inversion Port 0 Register

| Bit     | 7    | 6    | 5    | 4    | 3    | 2    | 1    | 0    |
|---------|------|------|------|------|------|------|------|------|
| Symbol  | N0.7 | N0.6 | N0.5 | N0.4 | N0.3 | N0.2 | N0.1 | N0.0 |
| Default | 0    | 0    | 0    | 0    | 0    | 0    | 0    | 0    |

Table 6-8. Polarity Inversion Port 1 Register

| Bit     | 7    | 6    | 5    | 4    | 3    | 2    | 1    | 0    |
|---------|------|------|------|------|------|------|------|------|
| Symbol  | N1.7 | N1.6 | N1.5 | N1.4 | N1.3 | N1.2 | N1.1 | N1.0 |
| Default | 0    | 0    | 0    | 0    | 0    | 0    | 0    | 0    |

#### 6.5.6. Registers 6 and 7: Configuration registers

This register pair configures the directions of the I/O pins. If a bit in this register is set (written with 1), the corresponding port pin is enabled as an input with high-impedance output driver. If a bit in this register is cleared (written with 0), the corresponding port pin is enabled as an output.

Table 6-9. Configuration Port 0 Register

| Bit     | 7    | 6    | 5    | 4    | 3    | 2    | 1    | 0    |
|---------|------|------|------|------|------|------|------|------|
| Symbol  | C0.7 | C0.6 | C0.5 | C0.4 | C0.3 | C0.2 | C0.1 | C0.0 |
| Default | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 1    |

Table 6-10. Configuration Port 1 Register

{18}------------------------------------------------

| Bit     | 7    | 6    | 5    | 4    | 3    | 2    | 1    | 0    |
|---------|------|------|------|------|------|------|------|------|
| Symbol  | C1.7 | C1.6 | C1.5 | C1.4 | C1.3 | C1.2 | C1.1 | C1.0 |
| Default | 1    | 1    | 1    | 1    | 1    | 1    | 1    | 1    |

## 6.6. Bus Transactions

#### 6.6.1. Writing to the Port Registers

Data is transmitted to the NCA9539-Q1 by sending the device address and setting the least significant bit to a logic 0 (see Figure 6-8). The command byte is sent after the address and determines which register will receive the data following the command byte.

The eight registers within the NCA9539-Q1 are configured to operate as four register pairs. The four pairs are Input Ports, Output Ports, Polarity Inversion Ports, and Configuration Ports. After sending data to one register, the next data byte will be sent to the other register in the pair (see Figure 6-10 and Figure 6-11). For example, if the first byte is sent to Output Port 1 (register 3), then the next byte will be stored in Output Port 0 (register 2).

There is no limitation on the number of data bytes sent in one write transmission. In this way, each 8-bit register may be updated independently of the other registers.

![Timing diagram for writing to output port registers. It shows SCL and SDA lines. The sequence starts with a START condition, followed by a slave address (bits 1-7: 1110101, bit 8: R/W=0, bit 9: Acknowledge). Then a Command byte (00000110) is sent and acknowledged. Next, Data to port 0 (0.7, DATA 0, 0.0) is sent and acknowledged. Finally, Data to port 1 (1.7, DATA 1, 1.0) is sent and acknowledged, followed by a STOP condition. Below the SDA line, 'Write to port' is high. 'Data out from port 0' and 'Data out from port 1' show transitions to 'DATA VALID' after their respective acknowledgments, with a delay labeled tv(Q).](09ab686699bb9597b8025e78fb390069_img.jpg)

Timing diagram for writing to output port registers. It shows SCL and SDA lines. The sequence starts with a START condition, followed by a slave address (bits 1-7: 1110101, bit 8: R/W=0, bit 9: Acknowledge). Then a Command byte (00000110) is sent and acknowledged. Next, Data to port 0 (0.7, DATA 0, 0.0) is sent and acknowledged. Finally, Data to port 1 (1.7, DATA 1, 1.0) is sent and acknowledged, followed by a STOP condition. Below the SDA line, 'Write to port' is high. 'Data out from port 0' and 'Data out from port 1' show transitions to 'DATA VALID' after their respective acknowledgments, with a delay labeled tv(Q).

Figure 6-10. Write to output port registers

![Timing diagram for writing to config registers. It shows SCL and SDA lines. The sequence starts with a START condition, followed by a slave address (bits 1-7: 1110101, bit 8: R/W=0, bit 9: Acknowledge). Then a Command byte (00000110) is sent and acknowledged. Next, Data to register (DATA 0) is sent and acknowledged. Then, another Data to register (DATA 1) is sent and acknowledged, followed by a STOP condition. The 'Data out' line shows a transition to 'DATA VALID' after the second acknowledgment, with a delay labeled tv(Q).](4e7f11ebd82a34bb69e271477038b901_img.jpg)

Timing diagram for writing to config registers. It shows SCL and SDA lines. The sequence starts with a START condition, followed by a slave address (bits 1-7: 1110101, bit 8: R/W=0, bit 9: Acknowledge). Then a Command byte (00000110) is sent and acknowledged. Next, Data to register (DATA 0) is sent and acknowledged. Then, another Data to register (DATA 1) is sent and acknowledged, followed by a STOP condition. The 'Data out' line shows a transition to 'DATA VALID' after the second acknowledgment, with a delay labeled tv(Q).

Figure 6-11. Write to config registers

#### 6.6.2. Reading the Port Registers

In order to read data from the NCA9539-Q1, the bus master must first send the NCA9539-Q1 address with the least significant bit set to a logic 0 (see Figure 6-8). The command byte is sent after the address and determines which register will be accessed. After a restart, the device address is sent again, but this time the least significant bit is set to a logic 1. Data from the register defined by the command byte will then be sent by the NCA9539-Q1 (see Figure 6-12, Figure 6-13 and Figure 6-14). Data is clocked into the register on the rising edge of the acknowledge clock pulse. After the first byte is read, additional bytes may be read but the data will now reflect the information in the other register in the pair. For example, if Input Port 1 is read, then the next byte read would be Input

{19}------------------------------------------------

Port 0. There is no limitation on the number of data bytes received in one read transmission, but the final byte received, the bus master must not acknowledge the data.

![Timing diagram for reading from registers. It shows two sequences of SDA signals. The first sequence starts with a START condition (S), followed by a slave address (11101), a read/write bit (A1), and an acknowledge (A0). This is followed by a COMMAND BYTE and another acknowledge (A). The second sequence starts with a repeated START condition (S), followed by the slave address (11101), a read/write bit (A1), and an acknowledge (A0). This is followed by data bytes (DATA (first byte) and DATA (last byte)). The master acknowledges the first byte and does not acknowledge the last byte, followed by a STOP condition (P). Labels indicate 'slave address', 'START condition', 'R/W', 'Acknowledge from slave', 'COMMAND BYTE', 'Data from lower or upper byte of register', 'MSB', 'LSB', 'DATA (first byte)', 'DATA (last byte)', 'Acknowledge from master', 'No acknowledge from master', and 'STOP condition'. A note states: 'At this moment master-transmitter becomes master-receiver and slave-receiver becomes slave-transmitter'.](81a4cbf0b3c4cbc065efdf8f800dadde_img.jpg)

Timing diagram for reading from registers. It shows two sequences of SDA signals. The first sequence starts with a START condition (S), followed by a slave address (11101), a read/write bit (A1), and an acknowledge (A0). This is followed by a COMMAND BYTE and another acknowledge (A). The second sequence starts with a repeated START condition (S), followed by the slave address (11101), a read/write bit (A1), and an acknowledge (A0). This is followed by data bytes (DATA (first byte) and DATA (last byte)). The master acknowledges the first byte and does not acknowledge the last byte, followed by a STOP condition (P). Labels indicate 'slave address', 'START condition', 'R/W', 'Acknowledge from slave', 'COMMAND BYTE', 'Data from lower or upper byte of register', 'MSB', 'LSB', 'DATA (first byte)', 'DATA (last byte)', 'Acknowledge from master', 'No acknowledge from master', and 'STOP condition'. A note states: 'At this moment master-transmitter becomes master-receiver and slave-receiver becomes slave-transmitter'.

**Remark:** Transfer of data can be stopped at any moment by a STOP condition.

Figure 6-12. Read from registers

![Timing diagram for reading input port registers, scenario 1. It shows the relationship between Data into port 0 (DATA 00, DATA 01, DATA 02, DATA 03), Data into port 1 (DATA 10, DATA 11, DATA 12), INT, SCL, SDA, Read from port 0, and Read from port 1. The SDA signal shows a sequence of START condition (S), slave address (11101), R/W bit, Acknowledge from slave (A), DATA 00, Acknowledge from master (A), DATA 10, Acknowledge from master (A), DATA 03, Acknowledge from master (A), DATA 12, Non acknowledge from master (NA), and STOP condition (P). Timing parameters like t_h(D), t_su(D), t_r(INT_N), and t_su(INT_N) are indicated. The Read from port 0 and Read from port 1 signals are shown as pulses corresponding to the data bytes.](2eb23c2210154279f8013a1594fbcc5a_img.jpg)

Timing diagram for reading input port registers, scenario 1. It shows the relationship between Data into port 0 (DATA 00, DATA 01, DATA 02, DATA 03), Data into port 1 (DATA 10, DATA 11, DATA 12), INT, SCL, SDA, Read from port 0, and Read from port 1. The SDA signal shows a sequence of START condition (S), slave address (11101), R/W bit, Acknowledge from slave (A), DATA 00, Acknowledge from master (A), DATA 10, Acknowledge from master (A), DATA 03, Acknowledge from master (A), DATA 12, Non acknowledge from master (NA), and STOP condition (P). Timing parameters like t\_h(D), t\_su(D), t\_r(INT\_N), and t\_su(INT\_N) are indicated. The Read from port 0 and Read from port 1 signals are shown as pulses corresponding to the data bytes.

**Remark:** Transfer of data can be stopped at any moment by a STOP condition. When this occurs, data present at the latest acknowledge phase is valid(output mode). It is assumed that the command byte has previously been set to '00' (read Input Port register).

Figure 6-13. Read input port registers, scenario 1

{20}------------------------------------------------

![Timing diagram for I2C read input port registers, scenario 2. It shows the relationship between Data into port 0, Data into port 1, INT, SCL, SDA, Read from port 0, and Read from port 1 signals. The SDA signal is detailed with a sequence of bytes: START condition (S), slave address (11101A1), R/W (1), Acknowledge from slave (A0), data byte I0.x (76543210), Acknowledge from master (A), data byte I1.x (76543210), Acknowledge from master (A), data byte I0.x (76543210), Acknowledge from master (A), data byte I1.x (76543210), Non acknowledge from master (N), and STOP condition (P). The INT signal is shown with rise and fall times t_r(INT_N) and t_f(INT_N).](2a77eb32ef4c4d8a5c1758a53a908336_img.jpg)

The timing diagram illustrates an I2C read operation from input port registers. The SDA signal sequence is as follows:
 

- S**: START condition
- 1 1 1 0 1 A 1**: slave address
- 1**: R/W bit
- A 0**: Acknowledge from slave
- 7 6 5 4 3 2 1 0**: data byte I<sub>0.x</sub>
- A**: Acknowledge from master
- 7 6 5 4 3 2 1 0**: data byte I<sub>1.x</sub>
- A**: Acknowledge from master
- 7 6 5 4 3 2 1 0**: data byte I<sub>0.x</sub>
- A**: Acknowledge from master
- 7 6 5 4 3 2 1 0**: data byte I<sub>1.x</sub>
- N**: Non acknowledge from master
- P**: STOP condition

Timing diagram for I2C read input port registers, scenario 2. It shows the relationship between Data into port 0, Data into port 1, INT, SCL, SDA, Read from port 0, and Read from port 1 signals. The SDA signal is detailed with a sequence of bytes: START condition (S), slave address (11101A1), R/W (1), Acknowledge from slave (A0), data byte I0.x (76543210), Acknowledge from master (A), data byte I1.x (76543210), Acknowledge from master (A), data byte I0.x (76543210), Acknowledge from master (A), data byte I1.x (76543210), Non acknowledge from master (N), and STOP condition (P). The INT signal is shown with rise and fall times t\_r(INT\_N) and t\_f(INT\_N).

**Remark:** Transfer of data can be stopped at any moment by a STOP condition. When this occurs, data present at the latest acknowledge phase is valid(output mode). It is assumed that the command byte has previously been set to '00' (read Input Port register).

Figure 6-14. Read input port registers, scenario 2

{21}------------------------------------------------

# 7. Application Design-In Information

## 7.1. Application Information

In applications of the NCA9539-Q1, the device is connected as a slave to an I2C controller (processor), and the I2C bus may contain any number of other slave devices. The NCA9539-Q1 is typically in a remote location from the master, placed close to the GPIOs to which the master needs to monitor or control.

IO Expanders such as the NCA9539-Q1 are typically used for controlling LEDs (for feedback or status lights), controlling enable or reset signals of other devices, and even reading the outputs of other devices or buttons.

## 7.2. Typical Application

![Figure 7-1: Typical Application circuit diagram showing the NCA9539-Q1 connected to a Master Controller via I2C (SCL, SDA) and control pins (INT, RESET). The NCA9539-Q1 is connected to various sub-systems: SUB-SYSTEM 1 (e.g., temp sensor) via INT, SUB-SYSTEM 2 (e.g., temp sensor) via RESET, a 10 DIGIT NUMERIC KEYPAD via P00-P17, and a Controlled switch (e.g., CBT device) via P04 and P05. The Master Controller is connected to VDD (3.6 V) and GND. The NCA9539-Q1 is connected to VDD and VSS. Pull-up resistors (10KΩ) are connected to the SCL, SDA, INT, and RESET pins. Pull-down resistors (2KΩ) are connected to the P00 and P01 pins. The 10 DIGIT NUMERIC KEYPAD is connected to the P00-P17 pins via address lines A0 and A1.](90ddf538ef276510e2b631f7b96654e6_img.jpg)

Figure 7-1: Typical Application circuit diagram showing the NCA9539-Q1 connected to a Master Controller via I2C (SCL, SDA) and control pins (INT, RESET). The NCA9539-Q1 is connected to various sub-systems: SUB-SYSTEM 1 (e.g., temp sensor) via INT, SUB-SYSTEM 2 (e.g., temp sensor) via RESET, a 10 DIGIT NUMERIC KEYPAD via P00-P17, and a Controlled switch (e.g., CBT device) via P04 and P05. The Master Controller is connected to VDD (3.6 V) and GND. The NCA9539-Q1 is connected to VDD and VSS. Pull-up resistors (10KΩ) are connected to the SCL, SDA, INT, and RESET pins. Pull-down resistors (2KΩ) are connected to the P00 and P01 pins. The 10 DIGIT NUMERIC KEYPAD is connected to the P00-P17 pins via address lines A0 and A1.

Figure 7-1. Typical Application

# 8. Order Information

| Part No.       | Temperature  | MSL Level | Package Type | Package Drawing | Package Qty |
|----------------|--------------|-----------|--------------|-----------------|-------------|
| NCA9539-Q1TSXR | -40 to 125°C | 1         | TSSOP24      | TSSOP24         | 2500        |

NOTE: All packages are RoHS-compliant with peak reflow temperatures of 260 °C according to the JEDEC industry standard classifications and peak solder temperatures.

{22}------------------------------------------------

# 9. Documentation Support

| <b><i>Part Number</i></b> | <b><i>Product Folder</i></b> | <b><i>Datasheet</i></b>    | <b><i>Technical Documents</i></b> | <b><i>Isolator selection guide</i></b> |
|---------------------------|------------------------------|----------------------------|-----------------------------------|----------------------------------------|
| NCA9539-Q1                | <a href="#">Click here</a>   | <a href="#">Click here</a> | <a href="#">Click here</a>        | <a href="#">Click here</a>             |

{23}------------------------------------------------

# 10. Package Information

![TSSOP24 Package Shape and Dimension diagrams including Top View, Side View, and Detail Z. A dimension table is provided on the right.](45329c7d9aa2bd1290af5b2027f08d7e_img.jpg)

**TOP VIEW**

**SIDE VIEW**

**DETAIL Z**

**\* CONTROLLING DIMENSION : MM**

| SYMBOL | MILLIMETER |      |      |
|--------|------------|------|------|
|        | MIN.       | NOM. | MAX. |
| A      | ---        | ---  | 1.10 |
| A1     | 0.05       | ---  | 0.15 |
| A2     | 0.80       | ---  | 0.95 |
| A3     | ---        | 0.25 | ---  |
| Q      | 0.30       | ---  | 0.40 |
| b      | 0.19       | 0.25 | 0.30 |
| c      | 0.10       | ---  | 0.20 |
| D      | 7.70       | 7.80 | 7.90 |
| E      | 4.30       | 4.40 | 4.50 |
| HE     | 6.20       | 6.40 | 6.60 |
| e      | 0.65 bsc   |      |      |
| L      | 1.00 bsc   |      |      |
| L1     | 0.50       | ---  | 0.75 |
| Y      | ---        | 0.10 | ---  |
| Z      | 0.2        | ---  | 0.5  |
| θ      | 0°         | ---  | 8°   |

**NOTES**  
1.0 COPLANARITY APPLIES TO LEADS, CORNER LEADS AND DIE ATTACH PAD.

TSSOP24 Package Shape and Dimension diagrams including Top View, Side View, and Detail Z. A dimension table is provided on the right.

Figure 10-1. TSSOP24 Package Shape and Dimension in millimeters

# 11. Tape and Reel Information

![Tape and Reel Information diagrams showing top and cross-sectional views of a tape with dimensions. Two dimension tables are provided on the right.](a1a474be12b8992842992294b1d18592_img.jpg)

**Top View Dimensions:** P0, P2, ΦD, ΦD1, B, B0, t, A0, P

**Cross-Sectional View Dimensions:** t, B0, K0, K1, A0, 4.7 ± 0.1, 4.3 ± 0.1, K0, 0.3

|      |              |    |              |
|------|--------------|----|--------------|
| E    | 1.75 ± 0.10  | W  | 16.00 ± 0.30 |
| F    | 7.5 ± 0.10   | P  | 8.00 ± 0.10  |
| P2   | 2.00 ± 0.10  | A0 | 6.80 ± 0.10  |
| D    | 1.55 ± 0.10  | B0 | 8.04 ± 0.10  |
| D1   | 1.55 ± 0.10  | K0 | 1.25 ± 0.10  |
| P0   | 4.00 ± 0.10  | K1 | 1.1 ± 0.10   |
| 10P0 | 40.00 ± 0.20 | t  | 0.30 ± 0.05  |
|      |              | θ  | 5° TYP       |

Tape and Reel Information diagrams showing top and cross-sectional views of a tape with dimensions. Two dimension tables are provided on the right.

NOTE: ALL DIMENSIONS IN MILLIMETERS UNLESS OTHERWISE STATED.

{24}------------------------------------------------

![Diagram showing quadrant designations and tape and reel information for TSSOP24.](552265bdbcf6d43d341fd018a9076269_img.jpg)

The diagram illustrates the orientation and placement of components on a tape and reel. On the left, a square is divided into four quadrants labeled 1, 2, 3, and 4, with the text 'Quadrant Designations' below it. On the right, a portion of a tape is shown with a 'Direction of Feed' arrow pointing right. The tape contains a row of eight circular pockets and two rectangular pockets, each with a black dot in its top-left corner.

Diagram showing quadrant designations and tape and reel information for TSSOP24.

Figure 11-1. Tape and reel information for TSSOP24

# 12. Revision History

| Revision | Description     | Date     |
|----------|-----------------|----------|
| 1.0      | Initial version | 2023/1/5 |

{25}------------------------------------------------

## **IMPORTANT NOTICE**

The information given in this document shall in no event be regarded as a guarantee of any warranty or authorization, express or implied, including but not limited to merchantability, fitness for a particular purpose or infringement of any third party's intellectual property rights.

You are solely responsible for your use of Novosense's products and applications. You shall comply with all laws, regulations and requirements related to Novosense's products and applications, although information or support related to any application may still be provided by Novosense.

The resources are intended only for skilled developers designing with Novosense's products. Novosense reserves the rights to make corrections, modifications, enhancements, improvements or other changes to the products and services provided. Novosense authorizes you to use these resources for the development of relevant applications of Novosense's products, other reproduction and display of these recourses is prohibited. Novosense shall not be liable for any claims, damages, costs, losses or liabilities arising out of the use of these resources.

For further information on applications, products and technologies, please contact Novosense ([www.novosns.com](http://www.novosns.com)).

Suzhou Novosense Microelectronics Co., Ltd