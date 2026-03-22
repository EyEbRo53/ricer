# System Utilities Dependency Flowchart

## Dependency Graph

```
┌─────────────────────────────────────────────────────────────────┐
│                    SESSION HANDLER                              │
│               (Lifecycle & Orchestration)                       │
└────┬──────────────────┬──────────────────┬──────────────────┬───┘
     │                  │                  │                  │
     ▼                  ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ CONFIG       │  │ STATE        │  │ TEMPLATE     │  │ FAILURE      │
│ CHECKER      │  │ MANAGER      │  │ MANAGER      │  │ HANDLER      │
│              │  │              │  │              │  │              │
│ • Verifies   │  │ • Tracks     │  │ • Records    │  │ • Logs       │
│   config     │  │   undo/redo  │  │   confirmed  │  │   execution  │
│   changes    │  │   stacks     │  │   changes    │  │   failures   │
│ • Uses SQLite│ │ • Persists   │  │ • Persists   │  │ • Dummy impl │
│ • No internal│  │   deltas     │  │   to SQLite  │  │   (stub)     │
│   deps       │  │ • No internal│  │ • No internal│  │ • No internal│
│              │  │   deps       │  │   deps       │  │   deps       │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
     ▲                  ▲                  ▲                  ▲
     │                  │                  │                  │
     └──────────────────┴──────────────────┴──────────────────┘
                        │
                 ┌──────┴──────┐
                 │             │
                 ▼             ▼
          ┌─────────────┐  ┌──────────────┐
          │ ORDER       │  │ External Deps│
          │ MANAGER     │  │              │
          │             │  │ • SQLite (DB)│
          │ • Executes  │  │ • KDE Config │
          │   changes   │  │   Reader     │
          │ • Wired via  │  │ • Scripts    │
          │   callbacks │  │   (/scripts/)│
          │ • Stateless  │  │              │
          │ • No imports │  └──────────────┘
          │   from utils │
          └─────────────┘
```

## Detailed Dependency Breakdown

### 1. **SessionHandler** (Central Orchestrator)

- **Role**: Lifecycle owner for a single MCP session
- **Dependencies**:
  - ✅ `ConfigChecker`
  - ✅ `StateManager`
  - ✅ `TemplateManager`
  - ✅ `FailureHandler`
  - ✅ `OrderManager`
  - ✅ `sqlite3` (external)
- **Responsibilities**:
  - Creates instances of all other utilities
  - Wires them together via callbacks
  - Owns the SQLite database connection
  - Manages session lifecycle

### 2. **OrderManager** (Change Executor)

- **Role**: Executes a single confirmed change
- **Dependencies**:
  - None from sibling utilities ✅
  - External: `importlib`, `sys`, `os` (standard library)
- **Design**:
  - Completely stateless between calls
  - Injected with 4 callbacks from SessionHandler
  - Isolation allows for independent testing and reusability

### 3. **ConfigChecker** (Verification Engine)

- **Role**: Verifies that script execution changed KDE config to expected values
- **Dependencies**:
  - None from sibling utilities ✅
  - External: KDE config reader utility via `utilities.kde_config_reader`
- **Design**:
  - Stateless
  - Maps script names to config verification rules
  - Returns `True` optimistically for DBus/kscreen-doctor scripts

### 4. **StateManager** (Undo/Redo Manager)

- **Role**: Tracks configuration state for undo/redo support
- **Dependencies**:
  - None from sibling utilities ✅
  - External: `sqlite3`, callbacks injected from SessionHandler
- **Responsibilities**:
  - Stores deltas (before → after values)
  - Manages undo/redo stacks
  - Persists deltas to SQLite for session survival

### 5. **TemplateManager** (Template Persistence)

- **Role**: Records and manages reusable change templates
- **Dependencies**:
  - None from sibling utilities ✅
  - External: `sqlite3`
- **Design**:
  - Only records confirmed & verified changes
  - Provides CRUD interface for templates
  - Persists to SQLite database

### 6. **FailureHandler** (Error Collector)

- **Role**: Collects execution failures for inspection
- **Dependencies**:
  - None from sibling utilities ✅
  - No external dependencies (currently)
- **Design**:
  - Dummy placeholder implementation
  - Future: Will add SQLite persistence
  - Currently logs failures in memory only

## Execution Flow (Single Change)

```
SessionHandler.confirm_change(receipt)
        │
        ├─→ OrderManager.execute()
        │       │
        │       ├─→ ConfigChecker.snapshot()  [BEFORE]
        │       │
        │       ├─→ [Import & execute script from /scripts/]
        │       │
        │       ├─→ ConfigChecker.verify()    [VERIFICATION]
        │       │
        │       ├─→ ON_SUCCESS:
        │       │   ├─→ StateManager.record() [DELTA]
        │       │   └─→ TemplateManager.append() [TEMPLATE]
        │       │
        │       └─→ ON_FAILURE:
        │           └─→ FailureHandler.log() [ERROR LOG]
        │
        └─→ Database operations (if needed)
```

## Key Architectural Patterns

### 1. **Dependency Injection**

- OrderManager receives callbacks instead of importing other utilities
- Enables testing and loose coupling

### 2. **Single Responsibility**

- Each utility has one core responsibility
- No circular dependencies
- Utilities can be used independently or together

### 3. **Callback Wiring**

```python
# SessionHandler wires callbacks at creation:
order = OrderManager(
    on_snapshot=config_checker.snapshot,
    on_verify=config_checker.verify,
    on_success=lambda c,b,a: [state_mgr.record(c,b,a),
                               template_mgr.append(c)],
    on_failure=failure_handler.log
)
```

### 4. **Shared Resources**

- All utilities share the same SQLite database connection (`ricer.db`)
- Session ID passed to utilities that need persistence
- Database path: `~/.config/ricer/ricer.db`

## Summary

- **0 circular dependencies** ✅
- **1 central orchestrator** (SessionHandler) that imports all others
- **5 leaf utilities** with zero inter-utility imports
- **Clean separation** of concerns with dependency injection pattern
- **Testable** components that can be used independently
