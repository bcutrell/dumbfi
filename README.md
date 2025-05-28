# DumbFi

A very much WIP retro-style stock trading simulator

## Built With

- Python frontend with Pyxel retro game engine
- Rust backend for using maturin

## Setup & Installation

```bash
pip install uv

# clone the repo
git clone https://github.com/yourusername/dumbfi.git
cd dumbfi

# sync the environment
uv sync -e .

# run the game
uv run dumbfi
```

## Rust Changes
```bash
# Changes to the extension code in lib.rs will require running --reinstall to rebuild them.
uv sync --reinstall
```

## How to Distribute

(from https://github.com/kitao/pyxel)
Pyxel supports a dedicated application distribution file format (Pyxel application file) that is cross-platform.

```bash
# Create a pyxel package
uv run pyxel package src src/dumbfi/app.py

# Run the package
uv run pyxel play src.pyxapp
```
