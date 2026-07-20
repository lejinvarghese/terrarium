# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Terrarium is a meta-project for orchestrating a local ecosystem of AI/ML services and nature-technology integrations. The focus is on service orchestration and management rather than custom application development.

**Core Services:**
- **Open WebUI**: Human-friendly interface for language models
- **ComfyUI**: Art generation using local or remote AI models (path configured via `COMFYUI_PATH` env var)
- **Ollama**: Local language model runtime

## Accessible Memories

For personal preferences and memories, refer to the `TERRARIUM_MEMORY.md` file. This file contains a log of my memories and your preferences.

## Multi-Landscape Architecture

The Terrarium is evolving toward a **multi-landscape ecosystem** where distinct civilizations of AI agents can emerge, interact, and migrate. See `docs/ARCHITECTURE.md` for the complete vision.

**Current Landscape: The Undergrowth**
- Culture: Dark, gothic, emergent, underground intelligence (urban hippie goth meets cyberpunk)
- Deployed bots: Anya, Nyx, Sage, Pepper, Cassia, Freya, Nigella, Casper
- Incubator agents: A001-A003 (training through RL exploration)

**Future**: Multiple biome-based landscapes (The Canopy, The Mycelium, The Reef, etc.) with distinct cultures, hive minds, and agent migrations between them.

## Architecture

This is primarily an orchestration project. The `src/` directory is currently empty and intended for automation scripts rather than a full application. Configuration is managed via `.env` file (gitignored for secrets and machine-specific settings).

### Service Locations

ComfyUI runs externally at a configurable location. Set `COMFYUI_PATH` environment variable to your ComfyUI installation directory (defaults to `~/projects/ComfyUI`).

## Development Commands

### Running ComfyUI
```bash
cd $COMFYUI_PATH  # or your ComfyUI installation directory
source .venv/bin/activate
python main.py
```

### Network Access

**Find local IP address:**
```bash
hostname -I
```

**Access services from other devices on local network:**
Navigate to `http://<IP_ADDRESS>:<PORT>` (e.g., `http://192.168.1.100:8080` for Open WebUI)

**Expose service to internet via tunnel:**
```bash
ssh -R 80:localhost:8080 ssh.localhost.run
```
This maps local port 8080 to a public URL provided by ssh.localhost.run.

## Technology Stack

Primary language: Python (for automation and orchestration scripts)
