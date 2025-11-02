# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Terrarium is a meta-project for orchestrating a local ecosystem of AI/ML services and nature-technology integrations. The focus is on service orchestration and management rather than custom application development.

**Core Services:**
- **Open WebUI**: Human-friendly interface for language models
- **ComfyUI**: Art generation using local or remote AI models (located at `/home/starscream/_projects/ComfyUI`)
- **Ollama**: Local language model runtime

## Architecture

This is primarily an orchestration project. The `src/` directory is currently empty and intended for automation scripts rather than a full application. Configuration is managed via `.env` file (gitignored for secrets and machine-specific settings).

### Service Locations

ComfyUI runs externally at `/home/starscream/_projects/ComfyUI`. **Note**: This path is hardcoded and may need adjustment for different environments.

## Development Commands

### Running ComfyUI
```bash
cd /home/starscream/_projects/ComfyUI
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
