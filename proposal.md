### Abstract

Ricing in the Linux community refers to extensively customizing a desktop environment’s appearance and layout, but the process remains difficult for beginners due to fragmented tooling, manual configuration, reliance on shell commands, and the risk of destabilizing the system. These challenges are especially prominent on Arch Linux, where flexibility often comes at the cost of usability and safety. This project proposes Ricer, an AI-assisted desktop customization framework for Arch Linux with KDE Plasma 6, aimed at lowering the technical barrier to controlled desktop personalization. Ricer allows users to describe desired visual and layout changes in natural language, which are translated into structured and deterministic customization workflows. An MCP (Model Context Protocol) server mediates between a large language model and system interfaces, ensuring that the AI suggests actions without directly executing system commands. The final outcome of the project is a desktop application that provides a conversational interface, a visual flowchart of applied changes, change management with rollback support, and template storage for customization workflows created within a single session, demonstrating a safe and extensible approach to AI-assisted desktop customization.

### 1. Introduction

The Linux desktop ecosystem is renowned for its unparalleled flexibility, giving rise to a vibrant culture of "ricing"—the art of extensively customizing a system’s aesthetics and workflow. For enthusiasts, ricing represents the ultimate expression of digital sovereignty. However, for new and intermediate users, this process remains gatekept by significant technical barriers. Achieving a cohesive "rice" typically requires manual editing of cryptic configuration files, navigating fragmented online forums, and executing complex shell commands that lack reliable safeguards or rollback mechanisms. On a rolling-release distribution like Arch Linux, this flexibility often comes at the cost of stability; a single unverified script or an incorrect D-Bus call can destabilize the entire desktop session.

This project proposes Ricer, an AI-assisted orchestration framework designed to bridge the gap between high-level user intent and low-level system configuration. Ricer transforms the customization experience into a conversational partnership. Instead of hunting for dotfiles, users describe their desired visual outcomes—such as "Apply a dark cyberpunk theme with a top-aligned dock"—in natural language.

Ricer acts as an intelligent intermediary, translating these requests into structured, auditable, and reversible actions. At its core, the system leverages the Model Context Protocol (MCP) to provide the AI with a "bounded authority". This ensures the AI understands the current state of the desktop—including active themes and window layouts—without having the permission to execute system commands directly. All proposed changes are instead validated by a dedicated backend and presented to the user for approval before execution.

While the underlying logic is extensible, the implementation of Ricer is intentionally focused on Arch Linux and KDE Plasma 6. This specific target allows the framework to leverage KDE’s mature D-Bus infrastructure and the robust kwriteconfig6 utility to ensure that customizations are applied deterministically and instantly. By prioritizing safety-first features like session-based snapshots and one-click rollbacks, Ricer aims to turn the volatile process of ricing into a safe, creative, and educational experience for all Linux users.

### 2. Goals and Objectives

1. **Conversational Interface:** Provide a natural-language chatbot that translates user intent into environment-aware plans via an LLM mediated by an MCP server.
2. **Safe Execution:** Require explicit session-level confirmation before applying changes, and rely on deterministic rollback to recover from unwanted results.
3. **Auditability & Recovery:** Capture session snapshots, manifests, and action logs for every customization session and implement deterministic rollback to restore prior state.
4. **Templating & Reuse:** Support creation, storage, and export of reusable “rice” templates (serialize both assets and action sequences) for personal reuse and community sharing.
5. **KDE Coverage:** Programmatically support themes, icons, fonts, panels/docks, widgets, window behavior, wallpapers, system sounds, accessibility settings, and preset layouts via KDE APIs (`kwriteconfig6`, D-Bus, Plasma scripting).
6. **Local-First Privacy:** Operate primarily on-device; if remote services are used, require explicit opt-in and document data flows.
7. **Usability Targets:** Deliver an intuitive flowchart/visualization of planned changes, a rollback manager UI, and clear help/guides.

### 3. Scope of the Project

The project scope for Ricer is strategically centered on Arch Linux and the KDE Plasma 6 environment to ensure high reliability and technical correctness. The framework's core functionality involves translating natural language intents into safe, structured customization actions, effectively acting as an intelligent intermediary that avoids system-breaking hallucinations by staying within the boundaries of established Plasma APIs. By focusing on Arch and KDE, the project leverages a mature theming infrastructure and a highly engaged ricing community, allowing for deep integration through tools like `kwriteconfig6` and D-Bus IPC.

The customization scope encompasses a wide range of visual and functional components, including global themes, accent colors, and transparency effects. Users can modify icons, cursors, and system-wide fonts, as well as the behavior and appearance of panels, docks, and desktop widgets. The framework also supports the configuration of window effects—such as wobbly windows and blur—alongside terminal aesthetics and performance-focused setting adjustments. Additionally, the scope includes the management of system sounds, wallpaper packs, and specific workspace elements like the clock, window titles, and the control center to provide a comprehensive ricing experience.

### 4. Initial Study and Work Done so Far

Initial development has focused on proving that KDE Plasma can be controlled programmatically without disrupting the user's session. We have successfully written scripts to change the **panel position** (top, bottom, left, and right) and the **desktop wallpaper**.

To achieve this, we utilized **PlasmaJS** to script the `plasmashell` and **gdbus** to trigger the changes through the system's D-Bus IPC. This method allows the environment to update instantly in real-time, removing the need to restart the shell or log out to see results.
