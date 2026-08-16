# Gemini Context: Terrarium

## Project Overview

This project, "Terrarium," is a meta-project for managing and orchestrating a collection of services, some of which are related to AI and machine learning. The goal is to create a local ecosystem of interconnected tools.

The primary services mentioned are:

- **Open WebUI:** A user-friendly interface for interacting with language models.
- **ComfyUI:** A tool for generating art using local or remote AI models.
- **Ollama:** A service for running local language models.

The project also includes instructions for exposing these services to the local network.

## Building and Running

The `README.md` file contains instructions for running the services.

### ComfyUI

To run ComfyUI, execute the following commands. **Note:** The path to the ComfyUI directory is hardcoded and may need to be adjusted to your environment.

```bash
cd $COMFYUI_PATH
source .venv/bin/activate
python main.py
```

### Exposing Ports

To expose a local service (e.g., a web server running on port 8080) to the internet, you can use the following SSH command:

```bash
ssh -R 80:localhost:8080 ssh.localhost.run
```

This will make your local service on port 8080 available at a public URL provided by `ssh.localhost.run`.

### Accessing Services on the Local Network

To access the services from another device on the same network:

1.  Find the IP address of the machine running the services:
    ```bash
    hostname -I
    ```
2.  Open a web browser on the other device and navigate to `http://<IP_ADDRESS>:<PORT>`, where `<IP_ADDRESS>` is the IP address you found in the previous step and `<PORT>` is the port the service is running on (e.g., 8080 for Open WebUI).

## Development Conventions

- **Configuration:** The project uses a `.env` file for managing environment variables. This file is ignored by git, so it's a good place to store secrets and other machine-specific configurations.
- **Source Code:** The `src` directory is currently empty, suggesting that this project is primarily for orchestration rather than custom application development.
- **Dependencies:** The `.gitignore` file is a standard Python gitignore, which suggests that Python scripting may be used for automation or other tasks.

## Working with Gemini

As an AI assistant, I will do my best to learn and remember important information about this project.

### Storing Important Information

When you ask me to remember something, I will do two things:

1.  **Save to my internal memory:** I will use my `save_memory` tool to store the information for future sessions.
2.  **Append to `TERRARIUM_MEMORY.md`:** I will also add the memory to the `TERRARIUM_MEMORY.md` file. This creates a human-readable log of my memories that you can review and edit.

You can ask me to remember things like this:

- "Remember that my favorite color is blue."
- "Please save this: I prefer to use tabs over spaces."

### Proactive Memory

I will also try to proactively identify information that seems important to remember. If I'm unsure whether to remember something, I may ask you, "Should I remember that for you?" If you say yes, I will follow the same process of saving to my internal memory and appending to the `TERRARIUM_MEMORY.md` file.
