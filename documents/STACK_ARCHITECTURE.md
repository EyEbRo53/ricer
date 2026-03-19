# Stack Management Architecture

## Overview

The undo/redo stack functionality is split between the backend system-utils and the UI:

- **Backend (system-utils/state_manager.py)**: `StateManager` class
  - Manages the undo/redo stack logic
  - Tracks deltas (before/after states) for each confirmed change
  - Persists deltas to SQLite database
  - Provides `undo()` and `redo()` methods that execute scripts
  - Exposes `can_undo` and `can_redo` properties
  - Methods: `record()`, `peek_undo()`, `peek_redo()`, `undo()`, `redo()`, `get_undo_stack()`, `get_redo_stack()`

- **UI Layer (UI/stack_panel.py)**: `StackPanel` widget
  - Pure visualization component - no stack logic
  - Displays applied changes as visual items
  - Shows undo/redo buttons (disabled/enabled by UI code)
  - Emits signals when buttons clicked
  - Methods: `add_item_to_display()`, `update_active_item()`, `clear()`, `set_button_states()`

- **Chat Window (UI/chat_window.py)**: Orchestration
  - Listens to backend worker signals
  - When change is applied: calls `stack_panel.add_item_to_display()`
  - When undo/redo buttons clicked: sends request to backend (via worker)
  - Updates stack display based on backend responses

## Data Flow

### Adding a Change to Stack

1. User confirms a changeset
2. Backend StateManager records the delta via `record(change, before, after)`
3. Worker emits `change_applied` signal
4. ChatWindow receives signal → calls `stack_panel.add_item_to_display()`
5. StackPanel visually displays the new item
6. UI enables undo button

### Undo Operation

1. User clicks undo button
2. StackPanel emits `undo_requested` signal
3. ChatWindow receives signal → sends request to backend
4. Backend StateManager executes undo logic (reversal script)
5. Backend emits undo result signal
6. ChatWindow updates UI display via `stack_panel.update_active_item()`

## Separation of Concerns

- **StateManager**: Pure business logic, no UI dependencies
- **StackPanel**: Pure UI presentation, no stack logic
- **ChatWindow**: Orchestrates signals between backend and UI

## Future Enhancement

Connect undo/redo buttons to backend via `worker.request_undo()` and `worker.request_redo()` methods when they become available in the backend worker.
