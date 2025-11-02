# Gemini Context: Terrarium

## Project Overview

This project, "Terrarium," is a meta-project for managing and orchestrating a collection of services, some of which are related to AI and machine learning. The goal is to create a local ecosystem of interconnected tools.

The primary services mentioned are:

*   **Open WebUI:** A user-friendly interface for interacting with language models.
*   **ComfyUI:** A tool for generating art using local or remote AI models.
*   **Ollama:** A service for running local language models.

The project also includes instructions for exposing these services to the local network.

## Building and Running

The `README.md` file contains instructions for running the services.

### ComfyUI

To run ComfyUI, execute the following commands. **Note:** The path to the ComfyUI directory is hardcoded and may need to be adjusted to your environment.

```bash
cd /home/starscream/_projects/ComfyUI
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

*   **Configuration:** The project uses a `.env` file for managing environment variables. This file is ignored by git, so it's a good place to store secrets and other machine-specific configurations.
*   **Source Code:** The `src` directory is currently empty, suggesting that this project is primarily for orchestration rather than custom application development.
*   **Dependencies:** The `.gitignore` file is a standard Python gitignore, which suggests that Python scripting may be used for automation or other tasks.

## Working with Gemini

As an AI assistant, I will do my best to learn and remember important information about this project.

### Storing Important Information

If you have specific details, conventions, or preferences that you want me to remember for future sessions, please let me know. You can say something like:

*   "Remember that all new services should be deployed on port 9000."
*   "Please save this: my preferred text editor is VS Code."

I will then use my `save_memory` tool to store this information.

### Proactive Memory

I will also try to proactively identify information that seems important to remember, such as:

*   Project-specific paths
*   Preferred libraries or frameworks
*   Commonly used commands

If I'm unsure whether to remember something, I may ask you, "Should I remember that for you?"
