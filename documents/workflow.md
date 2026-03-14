# Ricer MCP Server — Workflow Architecture

## 1. The Core Problem

The MCP server exposes tools that ultimately shell out to `kwriteconfig6`, `kscreen-doctor`, and DBus commands. These mutate the user's live desktop environment. **No command must execute without explicit user consent.**

The challenge is that in MCP, the **LLM** decides which tools to call — not the user directly. A naively designed server that executes on every tool call gives the LLM unchecked power over the user's session. We need an architecture that makes unconfirmed execution structurally impossible, not merely discouraged by a system prompt.

---

## 2. Design Principle: Plan Once, Confirm Each

The model is inspired by how GitHub Copilot handles terminal commands: the LLM proposes an action, but the action **blocks on user approval** before it touches anything. The user sees exactly what will happen and says yes or no — for every single change.

Applied to Ricer this becomes a **three-phase** pattern:

- **Phase 1 — Plan:** Tool calls do not execute anything. They build up an in-memory **changeset** (a staging area) on the server. The LLM presents the full plan so the user sees the big picture.
- **Phase 2 — Step-through:** The LLM walks through the changeset one change at a time. For each change, the user sees what will happen and explicitly confirms or skips it. Only confirmed changes execute.
- **Phase 3 — Finalize:** After all changes have been stepped through, the server handles reload/restart and persists the result as a reusable template.

This means even if the LLM misbehaves and calls tools eagerly, nothing touches the desktop until the user confirms individual changes via `confirm_change`. The changeset is inert data; each `confirm_change` call is a single, atomic, user-approved mutation.

---

## 3. Change Classification

Every tool is tagged with a **change type** that determines post-apply behaviour:

| Type      | What it means                                                                                                             | Examples                                                                                                                  | Post-apply action                                                    |
| --------- | ------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `display` | Change is visible immediately or after KWin reconfigure. No session restart needed.                                       | `set_global_scaling`, `set_window_borders`, `set_wallpaper`, `move_panel`                                                 | Call `reconfigure_kwin()` or nothing (DBus changes are already live) |
| `input`   | Change is written to a config file that applications only read at startup. Requires session restart to fully take effect. | `set_cursor_size`, `set_double_click_interval`, `set_single_click`, `set_touchpad_settings`, `set_keyboard_accessibility` | Inform user; offer restart options                                   |

A single changeset can contain both types. The post-apply logic must handle the **worst case** — if even one confirmed `input` change was applied, the user must be told about the restart requirement.

---

## 4. End-to-End Workflow

### Step 1 — User Prompt

The user writes a natural-language request to the LLM client (e.g. Claude Desktop, VS Code Copilot Chat):

> _"Make the desktop easier to use for someone with low vision — bigger cursor, larger borders, increase scaling"_

The LLM interprets intent. The MCP server does **not** do any planning or AI reasoning — it is a dumb tool provider.

### Step 2 — LLM Stages Changes (tool calls → changeset)

The LLM decides which tools to invoke and with what parameters. Each tool call lands in the server's changeset without executing:

```
LLM → tool: set_cursor_size(size=48)       → Server: adds to changeset
LLM → tool: set_window_borders(size="VeryLarge", snap_zone=16) → Server: adds to changeset
LLM → tool: set_global_scaling(factor=1.25) → Server: adds to changeset
```

Each tool returns a **staging receipt**, not an execution result. Each receipt references the underlying script to run and the parameters to pass — this is how the server knows what to execute when the user confirms. For example:

```json
{
  "status": "staged",
  "order": 1,
  "description": "Set cursor size to 48px",
  "change_type": "input",
  "script": "set_cursor_size",
  "parameters": {
    "size": 48
  }
}
```

The `script` field identifies which script in `/scripts/` will be invoked. The `parameters` field contains the exact arguments that will be passed to the script's main function. The MCP tool decides the parameter values; the script handles the actual KDE config writes.

The LLM accumulates these receipts. **Nothing has been executed.**

### Step 3 — LLM Presents the Full Plan

The LLM calls `review_changeset()` and presents the complete plan as an overview so the user understands the scope of what is about to happen:

> _Here's what I'd like to change:_
>
> 1. _Cursor size → 48px_ `[input — requires restart]`
> 2. _Window borders → VeryLarge, snap zone 16_ `[display — live]`
> 3. _Global scaling → 1.25×_ `[display — live]`
>
> _I'll go through each change one by one for your approval._

This is **informational only**. The user has not approved anything yet. The purpose is situational awareness — the user knows the full scope before being asked to approve individual items.

### Step 4 — Step-Through: Per-Change Confirmation

Now the LLM walks through the changeset sequentially. For each change, it presents the details and waits for user approval before calling `confirm_change`:

---

**Change 1 of 3:**

> _Set cursor size to 48px_
>
> - Script: `set_cursor_size`
> - Parameters: `size = 48`
> - Type: input (will require session restart)
> - Current value: 24
>
> _Apply this change?_

The user responds:

- **"yes"** → LLM calls `confirm_change(order=1)`. The server:
  1. Snapshots the current value before writing.
  2. Calls the `set_cursor_size` script with `size=48` via the orchestrator.
  3. Returns `{"status": "applied", "change_type": "input"}`.
- **"no" / "skip"** → LLM calls `skip_change(order=1)`. The server marks it as skipped. Nothing is written.

---

**Change 2 of 3:**

> _Set window borders to VeryLarge with snap zone 16_
>
> - Script: `set_window_borders`
> - Parameters: `border_size = "VeryLarge"`, `snap_zone = 16`
> - Type: display (live after KWin reload)
>
> _Apply this change?_

User: "yes" → `confirm_change(order=2)` → snapshot + execute via script.

---

**Change 3 of 3:**

> _Set global scaling to 1.25×_
>
> - Script: `set_global_scaling`
> - Parameters: `scale_value = 1.25`
> - Type: display (live immediately)
>
> _Apply this change?_

User: "yes" → `confirm_change(order=3)` → execute via script.

---

This per-change flow is analogous to how Copilot shows "Run this command in terminal?" before each shell command. The user retains granular control: they can approve some changes, skip others, and even abort mid-way through.

### Step 5 — Abort Mid-Way

At any point during the step-through, the user can say "stop" or "cancel the rest". The LLM calls `abort_remaining()`. Changes already confirmed and executed remain applied (they are already written). The user can later revert them via rollback tools. Unconfirmed changes are discarded.

### Step 6 — Finalize: Reload or Restart

After all changes have been stepped through (confirmed, skipped, or aborted), the LLM calls `finalize_changeset()`. The server inspects which changes were actually applied and their types:

**Case A — Only `display` changes were applied (or no changes at all):**

- Server calls `reconfigure_kwin()` from utilities.
- Returns success. User sees changes immediately. Done.

**Case B — At least one `input` change was applied:**

- Server calls `reconfigure_kwin()` first (so any confirmed `display` changes in the batch take effect immediately).
- Server returns a result listing the input changes that need a restart.
- The LLM presents options:

> _Display changes are live. The following changes need a session restart to take full effect:_
>
> - _Cursor size → 48px_
>
> _Options:_
>
> 1. _Restart later manually (changes will apply on next login)_
> 2. _Restart the environment now (⚠️ will close this application and all open applications)_

- If the user chooses option 2, the server calls the heavy reload path (`reload_kwin_and_plasma()` or `kquitapp6 plasmashell && kstart plasmashell`). The LLM client will likely crash — this is expected and the user was warned.

### Step 7 — Template Persistence

After finalization, the server automatically saves only the **confirmed and applied** changes as a **template**:

```json
{
  "template_id": "a1b2c3",
  "name": null,
  "created_at": "2026-03-06T14:30:00Z",
  "changes": [
    {
      "order": 1,
      "script": "set_cursor_size",
      "parameters": { "size": 48 },
      "change_type": "input"
    },
    {
      "order": 2,
      "script": "set_window_borders",
      "parameters": { "border_size": "VeryLarge", "snap_zone": 16 },
      "change_type": "display"
    },
    {
      "order": 3,
      "script": "set_global_scaling",
      "parameters": { "scale_value": 1.25 },
      "change_type": "display"
    }
  ]
}
```

Skipped changes are **not** included. The template represents what the user actually approved.

Templates are stored in `~/.config/ricer/templates/`.

The user can later:

- **Name a template:** `name_template(id="a1b2c3", name="Low Vision Profile")`
- **List templates:** `list_templates()` → returns all saved templates
- **Apply a template:** `apply_template(id="a1b2c3")` → loads the template into the changeset, then goes through the same step-through confirmation flow (Steps 4–6). The user can still skip individual changes when replaying a template.
- **Delete a template:** `delete_template(id="a1b2c3")`

Templates are the reusable "profiles" — e.g. a "Motor & Visual Decline" template, a "Default KDE" template, a "High Contrast" template.

---

## 5. Rollback

Every `confirm_change` snapshots the current value of the affected keys before writing. These per-change snapshots are aggregated into a session snapshot stored at `~/.config/ricer/state/<session_id>.json`.

- `revert_last()` — reverts the most recently finalized session by restoring all snapshots.
- `revert_to(session_id)` — reverts a specific session.
- Revert itself goes through per-change confirmation: the LLM presents each revert as a change, the user confirms or skips. This prevents accidental mass-reverts.

---

## 6. MCP Tool Surface

### Staging Tools (Phase 1 — no side effects)

These tools **only add entries to the in-memory changeset**. They never execute commands. Each tool corresponds to a script in `/scripts/` and returns a staging receipt containing the `script` name and `parameters` to pass when executed.

| Tool                                         | Script                       | Description                   | Change Type |
| -------------------------------------------- | ---------------------------- | ----------------------------- | ----------- |
| `set_cursor_size(size)`                      | `set_cursor_size`            | Stage cursor size change      | `input`     |
| `set_double_click_interval(interval)`        | `set_double_click_interval`  | Stage double-click interval   | `input`     |
| `set_single_click(enabled)`                  | `set_single_click`           | Stage single-click mode       | `input`     |
| `set_touchpad_settings(accel, speed, decel)` | `set_touchpad_settings`      | Stage touchpad tuning         | `input`     |
| `set_keyboard_accessibility(...)`            | `set_keyboard_accessibility` | Stage sticky/slow/bounce keys | `input`     |
| `set_global_scaling(factor)`                 | `set_global_scaling`         | Stage display scaling         | `display`   |
| `set_window_borders(size, snap_zone)`        | `set_window_borders`         | Stage window border size      | `display`   |
| `set_wallpaper(path)`                        | `set_wallpaper`              | Stage wallpaper change        | `display`   |
| `move_panel(position)`                       | `move_panel`                 | Stage panel position          | `display`   |

### Control Tools (Phase 2 — per-change execution)

| Tool                    | Description                                                                                                                                |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `review_changeset()`    | Return the full staged changeset for the LLM to present as an overview                                                                     |
| `confirm_change(order)` | Snapshot current value, then execute the staged change's script with its parameters. **This is the only tool that writes to the desktop.** |
| `skip_change(order)`    | Mark a staged change as skipped (will not execute)                                                                                         |
| `abort_remaining()`     | Skip all unconfirmed changes; move straight to finalization                                                                                |
| `finalize_changeset()`  | Handle KWin reload / restart prompt, save template, clear changeset                                                                        |
| `clear_changeset()`     | Discard all staged changes without executing anything                                                                                      |

### Template Tools

| Tool                      | Description                                                                 |
| ------------------------- | --------------------------------------------------------------------------- |
| `list_templates()`        | List all saved templates                                                    |
| `apply_template(id)`      | Load a template into the changeset (still requires per-change confirmation) |
| `name_template(id, name)` | Give a template a human-readable name                                       |
| `delete_template(id)`     | Delete a saved template                                                     |

### Rollback Tools

| Tool                    | Description                                                                     |
| ----------------------- | ------------------------------------------------------------------------------- |
| `list_snapshots()`      | List all saved state snapshots                                                  |
| `revert_last()`         | Load the most recent snapshot as a changeset (requires per-change confirmation) |
| `revert_to(session_id)` | Load a specific snapshot as a changeset (requires per-change confirmation)      |

---

## 7. Server State Model

The server maintains minimal in-memory state:

```
Server
├── changeset: List[ChangeEntry]     # currently staged changes
│   each entry has: order, script, parameters, change_type, status (staged|applied|skipped)
└── (disk)
    └── ~/.config/ricer/
        ├── state/                    # per-session snapshots (old values before changes)
        │   ├── a1b2c3.json
        │   └── d4e5f6.json
        └── templates/               # reusable templates (only confirmed changes)
            ├── a1b2c3.json
            └── d4e5f6.json
```

The changeset lives in memory and is lost if the server restarts. This is intentional — an uncommitted changeset should not survive a crash. Snapshots and templates are persisted to disk.

Each `ChangeEntry` tracks its own lifecycle:

```
staged  ──confirm_change──►  applied
   │
   └────skip_change───────►  skipped
```

---

## 8. Sequence Diagram

```
User            LLM (Client)         MCP Server            KDE Desktop
 │                  │                     │                      │
 │  "bigger cursor, │                     │                      │
 │   larger borders"│                     │                      │
 │─────────────────>│                     │                      │
 │                  │                     │                      │
 │                  │  set_cursor_size(48) │                      │
 │                  │────────────────────>│  [staged, order=1]   │
 │                  │  set_window_borders  │                      │
 │                  │  ("VeryLarge", 16)  │                      │
 │                  │────────────────────>│  [staged, order=2]   │
 │                  │                     │                      │
 │                  │  review_changeset() │                      │
 │                  │────────────────────>│                      │
 │                  │  [full plan]        │                      │
 │                  │<────────────────────│                      │
 │                  │                     │                      │
 │  "Plan: 2 changes│                     │                      │
 │   1. cursor 48px │                     │                      │
 │   2. borders XL" │                     │                      │
 │<─────────────────│                     │                      │
 │                  │                     │                      │
 │  ┌─── Per-change confirmation loop ──────────────────────┐   │
 │  │                                                        │   │
 │  │ "Change 1/2:   │                     │                 │   │
 │  │  cursor→48px.  │                     │                 │   │
 │  │  Apply?"       │                     │                 │   │
 │<─┤────────────────│                     │                 │   │
 │  │                │                     │                 │   │
 │  │ "yes"          │                     │                 │   │
 │──┤───────────────>│                     │                 │   │
 │  │                │  confirm_change(1)  │                 │   │
 │  │                │────────────────────>│                 │   │
 │  │                │                     │── kreadconfig6 >│ (snapshot)
 │  │                │                     │── kwriteconfig6>│ (write)
 │  │                │  {"applied",input}  │                 │   │
 │  │                │<────────────────────│                 │   │
 │  │                │                     │                 │   │
 │  │ "Change 2/2:   │                     │                 │   │
 │  │  borders→XL.   │                     │                 │   │
 │  │  Apply?"       │                     │                 │   │
 │<─┤────────────────│                     │                 │   │
 │  │                │                     │                 │   │
 │  │ "skip this one"│                     │                 │   │
 │──┤───────────────>│                     │                 │   │
 │  │                │  skip_change(2)     │                 │   │
 │  │                │────────────────────>│  [skipped]      │   │
 │  │                │<────────────────────│                 │   │
 │  │                                                        │   │
 │  └────────────────────────────────────────────────────────┘   │
 │                  │                     │                      │
 │                  │  finalize_changeset()│                      │
 │                  │────────────────────>│                      │
 │                  │                     │  (input change was   │
 │                  │                     │   applied → restart  │
 │                  │  {"restart_required",│   needed)            │
 │                  │   template saved}   │                      │
 │                  │<────────────────────│                      │
 │                  │                     │                      │
 │  "Cursor changed.│                     │                      │
 │   Borders skipped│                     │                      │
 │   Restart needed.│                     │                      │
 │   Now or later?" │                     │                      │
 │<─────────────────│                     │                      │
 │                  │                     │                      │
 │  "later"         │                     │                      │
 │─────────────────>│                     │                      │
 │  "OK. Will apply │                     │                      │
 │   on next login."│                     │                      │
 │<─────────────────│                     │                      │
```

---

## 9. Why This Works

1. **Per-change consent.** Every mutation is individually approved. The `confirm_change` tool is the only path to execution, and it applies exactly one change. The user sees what will happen — the script, its parameters, and the change type — before it touches the desktop. This mirrors the Copilot "run this command?" UX that users already understand.

2. **Granular control.** The user can approve change 1, skip change 2, approve change 3. The resulting template and snapshot reflect exactly what the user chose. Batch-confirm is an emergent behaviour (the user just says "yes" to each), not a separate code path.

3. **Structural safety.** Staging tools are inert by design. Even if the LLM calls every staging tool, the changeset is harmless data. The only tool with side effects is `confirm_change`, and it operates on a single entry at a time.

4. **Automatic rollback support.** Each `confirm_change` snapshots the current value before writing. The user never has to remember to save state — it happens atomically with every confirmed change.

5. **Templates reflect user intent.** Only confirmed changes are persisted to the template. If the user skipped border changes, the template won't include them. When replayed, the template goes through the same per-change confirmation, so the user can further customise.

6. **Change-type-aware finalization.** After the step-through, `finalize_changeset` knows exactly which change types were actually applied (not just staged). It only prompts for restart if an `input` change was confirmed, not merely proposed.

---

## 10. Limitations and Honest Trade-offs

- **The LLM is trusted to present each change.** If the LLM calls `confirm_change` in a loop without showing the user each step, changes will execute without informed consent. This is inherent to MCP — the server cannot verify what the user saw. Mitigation: tool descriptions that say "You MUST present the change details to the user and wait for their explicit approval before calling `confirm_change`." Additionally, MCP clients (like Claude Desktop) can be configured to require user approval on tool calls that have side effects — `confirm_change` should be marked as such.

- **Step-through can be tedious for large changesets.** If a profile has 9 changes, confirming each one individually is friction. This is an intentional trade-off: safety over speed. For the template-replay case, we could introduce a `confirm_all_remaining()` tool that the LLM offers after the first few changes — but only when replaying a previously-approved template, not for novel changes.

- **Input changes are disruptive.** There is no way around the fact that some KDE settings require a session restart. The best we can do is be transparent about it. Since the user confirms each input change individually, they know exactly which changes carry the restart cost.

- **Partial application is the normal case.** Unlike the old batch model, it is common for only some changes to be applied. The server, templates, and rollback logic must all handle partial changesets cleanly. This is more complex but more honest — it reflects what the user actually wanted.

- **Changeset is ephemeral.** If the server crashes mid-session, the staged changeset is lost. Already-confirmed changes survive (they are written to disk via `kwriteconfig6` and snapshotted). The user simply re-states their intent for the rest.

- **Template replay may drift.** A template saved today may not produce identical results on a different KDE version or hardware configuration. Templates store _intent_ (set cursor to 48px), not _state_ (the full system config). This is the correct trade-off for portability.

---

## 11. LLM Prompt Requirements

For this workflow to function correctly, the LLM client must be instructed with these behaviours. This should be part of the system prompt or MCP server tool descriptions:

1. **Always stage all changes first.** Do not call `confirm_change` until all relevant tools have been staged and the plan has been presented via `review_changeset`.

2. **Always present the full plan before stepping through.** Call `review_changeset` and show the user the complete list of proposed changes with their types.

3. **Walk through changes one at a time.** For each staged change, describe what it will do (script, parameters, change type) and ask the user to confirm or skip.

4. **Never call `confirm_change` without user approval.** Wait for an affirmative response ("yes", "ok", "do it", "apply") before invoking `confirm_change`.

5. **Call `finalize_changeset` after the step-through.** This handles reload, restart prompts, and template saving.

6. **If the user says "apply all" or "yes to everything", you may proceed through remaining changes without individual prompts** — but only if the user explicitly requested batch approval.
