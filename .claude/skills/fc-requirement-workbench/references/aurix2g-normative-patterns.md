# AURIX 2G 平台规范经验库

基于 FcStack AURIX2G 工程（G-Pulse G4 平台）提取的内置规范，用于需求生成时的模式参考和规则校验。

原始文件已拆分为三个子文件，按需加载：

- **[接口与多核模式](platform/interface-patterns.md)** — 驱动接口分类法则、MainFunction 规则、信号 ID 设计、状态机模式、多核架构与同步机制
- **[平台架构模式](platform/architecture-patterns.md)** — 配置需求规范（三件套、容器分级、预编译开关）、安全需求规范（SafeTpack、WDG、故障处理、复位管理）、状态管理需求规范
- **[驱动经验库](platform/driver-experience-library.md)** — 诊断需求规范、时序需求规范、8 种驱动类型经验库（CAN/LIN 收发器、电机驱动、PMIC、ADC、PWM、DIO、ICU、I2C GPIO）、命名与编码规范、需求校验检查清单

当只需要特定领域的平台规范时，直接加载对应子文件；当需要全量平台规范时，加载本索引文件并跟随子文件链接。
