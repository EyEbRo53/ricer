# Ricer

## Prerequisites

Install uv:

```bash
sudo pacman -S uv
```

Or with curl:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Setup

1. Create and activate virtual environment:

```bash
uv venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
uv pip install -e ricer-client
uv pip install -e ricer-mcp
uv pip install PySide6
```

## Run

```bash
python UI/main.py
```
