# Repository Guidelines

## Project Structure & Module Organization
- Keep automation code and shared utilities in `src/`, grouping modules by service (e.g., `src/open_webui/`, `src/comfyui/`).
- Documentation and agent playbooks live at the repository root (`README.md`, `CLAUDE.md`, `GEMINI.md`). Add new top-level docs here for quick discovery.
- Store machine-specific settings in `.env` (already gitignored). Provide a `.env.example` whenever you add configuration keys.

## Build, Test, and Development Commands
- Use Python 3.11+ virtual environments for tooling:
  ```bash
  python -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```
  Update `requirements.txt` when new dependencies are introduced.
- Follow the service launch flows in `README.md` when validating integrations (e.g., start ComfyUI via `python main.py` in `/home/starscream/_projects/ComfyUI`).
- Run smoke checks for network exposure with:
  ```bash
  hostname -I
  ssh -R 80:localhost:8080 ssh.localhost.run
  ```
  Record exposed ports in your change description.

## Coding Style & Naming Conventions
- Follow PEP 8 with 4-space indentation, `snake_case` for modules/functions, and `CamelCase` for classes.
- Add type hints for public functions and docstrings where orchestration steps are non-obvious.
- Format code with `ruff format` or `black` before submission, and lint with `ruff check` if available; include setup instructions when adding new tooling.

## Testing Guidelines
- Use `pytest` for automation coverage, mirroring source layout under `tests/` (e.g., `tests/open_webui/test_sync.py`). Name files `test_<feature>.py` and functions `test_<behavior>()`.
- Keep tests fast and environment-aware; gate external calls behind feature flags or mocks. Run suites with:
  ```bash
  pytest --maxfail=1 --disable-warnings
  ```
- Target meaningful coverage for orchestration logic and document required fixtures in the test module docstring.

## Commit & Pull Request Guidelines
- Write concise, imperative commit subjects capped at ~72 characters (e.g., `Add Open WebUI sync task`). Group related changes to avoid noisy diffs.
- Pull requests should include a purpose summary, affected services, testing evidence, and any local-network considerations.
- Link to tracking issues when available and attach screenshots or logs for UI-facing changes. Request review from service owners noted in the relevant documentation.

## Security & Configuration Tips
- Never commit secrets; reference environment variables instead. Rotate credentials immediately if exposure is suspected and log the action in the PR.
- When introducing network tunnels or exposed ports, document default bindings and remediation steps in the PR to keep the ecosystem safe.

## Accessible Memories

For personal preferences and memories, refer to the `TERRARIUM_MEMORY.md` file. This file contains a log of my memories and your preferences.
