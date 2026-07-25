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

**Ollama** models are stored on the fast SSD at `/media/starscream/bumblebee1/ollama/.ollama/models` (configured via systemd service environment variable).

## Storage Organization

To prevent root partition (`/`) from filling up, follow this storage strategy:

### Drive Allocation (as of 2026-07-24)

| Drive | Mount | Capacity | Free | Type | Purpose |
|-------|-------|----------|------|------|---------|
| nvme0n1p7 | `/media/starscream/bumblebee1` | 268GB | 237GB | NVMe SSD | **Primary workspace** - Active projects, Ollama models, fast I/O |
| sda6 | `/home` | 183GB | 78GB | HDD | User files, configs, small projects |
| sda5 | `/media/starscream/ironhide` | 319GB | 174GB | HDD | Large datasets, archives, media |
| nvme0n1p3 | `/media/starscream/megatron` | 187GB | 88GB | NVMe SSD | Fast scratch space, builds |
| sda2 | `/media/starscream/wheeljack1` | 280GB | 93GB | HDD | General storage |
| sda4 | `/` (root) | 144GB | 55GB | HDD | **System only** - keep minimal |

### Storage Guidelines

**Root partition (/)** - Keep under 70% usage:
- System files only - no user data or large applications
- Auto-cleanup runs weekly (Sundays 3am) via `/usr/local/bin/system-cleanup`
- Keeps journal logs for 7 days, temp files cleaned, old kernels removed

**bumblebee1 (primary SSD)** - Use for:
- Active development projects (like this Terrarium project)
- Ollama models (16GB currently, configured via `OLLAMA_MODELS=/media/starscream/bumblebee1/ollama/.ollama/models`)
- Anything needing fast I/O

**ironhide (large HDD)** - Use for:
- Large datasets, training data
- Video/media files
- Long-term archives
- Docker volumes for data-heavy services

**megatron (fast SSD)** - Use for:
- Build artifacts, compilation outputs
- Temporary ML model training
- Cache directories for development tools

**DO NOT store on root (/)**:
- Ollama models (moved to bumblebee1)
- Large Python virtual environments
- Docker images/containers (move to ironhide if needed)
- Media files, datasets, archives

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
