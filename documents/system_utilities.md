# Internal Utilities

These utilities implement the internal machinery behind the MCP server's `confirm_change → finalize_changeset` flow described in `workflow.md`. The workflow document defines the _external-facing_ protocol (staging, per-change confirmation, templates); this document defines the _internal components_ that make that protocol work.

---

## Design Principles

1. **Independence.** Each utility is a standalone module with no imports from sibling utilities. They communicate exclusively through the data they accept and return — never by reaching into each other's internals.

2. **Injection over coupling.** The Session Handler wires utilities together at session creation by passing callbacks. The Order Manager, for example, never imports `StateManager` — it receives an `on_success` callable that the Session Handler happens to bind to `state_manager.record`. This means any utility can be tested, replaced, or stubbed in isolation.

3. **Single direction of dependency.** Session Handler depends on all utilities (it creates them). Order Manager depends on injected callables. Every other utility depends on nothing.

```
Session Handler
├── creates → Order Manager (receives callbacks)
├── creates → State Manager
├── creates → Config Checker
├── creates → Template Manager
└── creates → Failure Handler
```

---

## 1. Session Handler

**Role:** Lifecycle owner. Every MCP server session maps to exactly one Session Handler instance, which owns one instance of each utility below.

**Responsibilities:**

- On session start: create all utility instances, wire callbacks, instruct State Manager to take an initial snapshot.
- On session end: persist the template (via Template Manager), flush failure logs, clean up in-memory state.
- Expose the undo/redo interface to the MCP control layer by delegating to State Manager.

**Storage root:** `~/.config/ricer/sessions/<session_id>/`

```
~/.config/ricer/sessions/<session_id>/
├── state/           # State Manager writes here
│   └── initial.json
├── template.json    # Template Manager writes here
└── failures.log     # Failure Handler writes here
```

**What it does NOT do:** It does not execute scripts, verify config, or manage changesets. It is purely a container and wiring layer.

---

## 2. Order Manager

**Role:** Executes a single confirmed change. This is the implementation behind `confirm_change(order)` from the MCP control layer.

**Input:** A `ChangeEntry` from the `Changeset` (the staging area defined in `changeset.py`).

**Execution flow for one confirmed change:**

```
1. Snapshot current value    → calls on_snapshot(change) callback
2. Execute the script        → calls kde_config_orchestrator
3. Verify the change took    → calls on_verify(change) callback
4. If verified:
     → calls on_success(change)     [State Manager records delta, Template Manager appends]
5. If verification failed:
     → retry once
     → if still failed: calls on_failure(change)    [Failure Handler logs it]
     → mark change as "failed" and return failure to MCP control layer
```

**Key design decisions:**

- Order Manager does NOT hold references to State Manager, Template Manager, Config Checker, or Failure Handler. It holds four callables: `on_snapshot`, `on_verify`, `on_success`, `on_failure` — injected by Session Handler at creation.
- Retry logic is limited to a single retry. If both attempts fail, the change is reported and the step-through continues to the next change (the user is informed).
- Order Manager is stateless between calls — each `execute(change)` is independent.

---

## 3. State Manager

**Role:** Tracks configuration state for undo/redo support.

**Behaviour:**

- **On session start:** Takes a full snapshot of all relevant KDE config keys (by calling each script's corresponding `get` resource). This is the baseline. Stored as `initial.json`.
- **On each confirmed change:** Stores only the delta — the keys that were expected to change, with their before and after values. This avoids re-snapshotting the entire config on every change.
- **Undo/redo stacks:** Deltas are pushed onto two stacks:

```
Undo Stack (applied changes, newest on top)
┌─────────────────────┐
│ Δ3: scaling 1.0→1.25│  ← most recent
│ Δ2: borders N→VL    │
│ Δ1: cursor 24→48    │
└─────────────────────┘

Redo Stack (reverted changes, available for restore)
┌─────────────────────┐
│  (empty until undo)  │
└─────────────────────┘
```

- **Undo:** Pops from Undo stack, restores the "before" values via the orchestrator, pushes the delta onto Redo stack.
- **Redo:** Pops from Redo stack, re-applies the "after" values, pushes back onto Undo stack.
- **Any new change clears the Redo stack** (same semantics as text editor undo — branching discards the redo future).

**Interface:**

- `take_initial_snapshot() → None` — called once per session.
- `record(change, before, after) → None` — called by Order Manager (via callback) after a verified change.
- `undo() → Delta | None` — reverts the most recent change.
- `redo() → Delta | None` — restores the most recently undone change.
- `get_full_state() → dict` — reconstructs current state by applying all undo-stack deltas to the initial snapshot.

**What it does NOT know about:** Orders, templates, failures, sessions. It is given data and manages stacks.

---

## 4. Config Checker

**Role:** Verifies that a script execution actually changed the KDE config to the expected value. This is a stateless verification utility.

**How it works:**

1. Receives: script name, parameters, expected outcome.
2. Calls the corresponding MCP resource's `get` function (e.g., for `set_cursor_size`, it reads the current cursor size via `kreadconfig6`).
3. Compares the current value against the expected value from the parameters.
4. Returns `pass` or `fail`.

**Change-type considerations:**

| Change Type | Verification Timing         | Notes                                                                                                                                                    |
| ----------- | --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `display`   | Immediately after execution | Value should be readable via `kreadconfig6` or `kscreen-doctor` right away.                                                                              |
| `input`     | Immediately after execution | The config _file_ is written immediately (verifiable). The _effect_ requires restart — but the checker verifies the config write, not the visual effect. |

**Interface:**

- `verify(script: str, parameters: dict) → bool`

**What it does NOT do:** It does not decide what to do about failures — it just returns a boolean. The Order Manager decides whether to retry or report.

---

## 5. Template Manager

**Role:** Records confirmed changes in execution order and persists them as a reusable template.

**Behaviour:**

- Maintains an ordered list of confirmed changes during the session.
- On `append(change)`: adds the change to the list.
- On `save()`: writes the template to disk.
- On `load(template_id)`: reads a template and returns it as a list of changes that can be fed back into the Changeset for replay.

**Template schema:**

```json
{
  "template_id": "a1b2c3",
  "session_id": "s9x8y7",
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
    }
  ]
}
```

- Only **confirmed and verified** changes appear in the template. Skipped, failed, and aborted changes are excluded.
- Templates are stored at `~/.config/ricer/sessions/<session_id>/template.json` (session-local) and optionally copied to `~/.config/ricer/templates/` (global, for cross-session reuse).

**Interface:**

- `append(change: dict) → None`
- `save(session_id: str) → str` — returns the template_id.
- `load(template_id: str) → list[dict]` — returns the ordered change list.
- `list_all() → list[dict]` — returns metadata for all saved templates.
- `rename(template_id: str, name: str) → None`
- `delete(template_id: str) → None`

**What it does NOT know about:** Whether a change was verified, retried, or how it was executed. It receives a confirmed change dict and appends it.

---

## 6. Failure Handler

**Role:** Logs execution failures to disk for debugging and user transparency.

**What gets logged:**

- Script name and parameters that were attempted.
- Error type: `verification_failed` (config did not change), `script_error` (subprocess crashed), `retry_exhausted` (failed after retry).
- Timestamp.
- Session ID.

**Log format (JSONL — one JSON object per line):**

```json
{
  "timestamp": "2026-03-06T14:31:12Z",
  "session_id": "s9x8y7",
  "script": "set_cursor_size",
  "parameters": { "size": 48 },
  "error_type": "verification_failed",
  "detail": "Expected cursor size 48, got 24"
}
```

**Storage:** `~/.config/ricer/sessions/<session_id>/failures.log`

**Interface:**

- `log(change: dict, error_type: str, detail: str) → None`
- `get_failures(session_id: str) → list[dict]` — reads and returns all failures for a session.

**What it does NOT do:** It does not retry, escalate, or make decisions. It writes to a file. The Order Manager decides what to do about failures before and after logging them.

---

## Wiring: How Session Handler Connects Everything

At session creation, Session Handler assembles the utilities and injects dependencies as callbacks:

```python
# Pseudo-code — illustrates the wiring pattern, not literal implementation

state_mgr       = StateManager(session_path / "state")
config_checker  = ConfigChecker()
template_mgr    = TemplateManager(session_path / "template.json")
failure_handler = FailureHandler(session_path / "failures.log")

order_mgr = OrderManager(
    on_snapshot = lambda change: state_mgr.snapshot_keys(change),
    on_verify   = lambda change: config_checker.verify(change["script"], change["parameters"]),
    on_success  = lambda change, before, after: (
        state_mgr.record(change, before, after),
        template_mgr.append(change),
    ),
    on_failure  = lambda change, error_type, detail: (
        failure_handler.log(change, error_type, detail),
    ),
)
```

This means:

- **Order Manager** has zero imports from other utilities — only callables.
- **State Manager, Config Checker, Template Manager, Failure Handler** have zero knowledge of each other.
- **Session Handler** is the only component that knows the full topology.
- Any utility can be unit-tested by passing mock callables or calling its methods directly with test data.
