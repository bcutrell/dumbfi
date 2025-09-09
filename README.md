# DumbFi

A very much WIP retro-style stock trading simulator

## Built With

- Python frontend with Pyxel retro game engine

## Setup & Installation

```bash
pip install uv

# clone the repo
git clone https://github.com/bcutrellyourusername/dumbfi.git
cd dumbfi

# sync the environment
uv sync -e .

# run the game
uv run dumbfi
```

## CLI
```
cd cli && npm run build && node dist/cli.js
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
