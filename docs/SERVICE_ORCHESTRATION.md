# Service Orchestration

Detailed guide for running and managing all Terrarium services, including optional components like ComfyUI, Ollama, and network access.

## Core Services

These run via `./dev up`:

### 🔮 Dome (Open WebUI)
Human-friendly interface for language models. Web-based chat with all your bots.

```bash
./app.sh
# or: dev attach dome
```

**Access:** http://localhost:8080

**Features:**
- Chat with all bots
- Model management
- Document upload
- Memory management

---

### 🌉 Portal (Telegram Bot)
Mobile gateway to your terrarium. Chat with Casper and route to specialized bots.

```bash
python3 -m src.portals.telegram.bot
# or: dev attach portal
```

**Setup:**
1. Create bot via [@BotFather](https://t.me/BotFather)
2. Get your chat ID via [@userinfobot](https://t.me/userinfobot)
3. Add to `.env`:
   ```bash
   TELEGRAM_TOKEN=your_bot_token
   TELEGRAM_CHAT_ID=your_chat_id
   ```

**Commands:**
- Direct message → Casper (general assistant)
- `/anya` → Creative director
- `/pepper` → Productivity coach
- `/nigella` → Culinary guide
- `/sage` → Strategic advisor
- `/nyx` → Tech futurist
- `/freya` → Health coach

---

### ⚙️ Engine (Scheduler)
The heartbeat. Runs automated tasks on schedule (morning briefings, health check-ins, etc.)

```bash
python3 src/engine/scheduler.py
# or: dev attach engine
```

**Configure:** Edit `src/configs/schedule.json`

**Features:**
- Human-readable schedules (`"every day at 07:00"`)
- Visual feedback (colorful banner, spinner)
- Non-interactive Claude CLI execution
- Task logging

---

### 🌐 Web Interface
Visual dashboard for the terrarium ecosystem.

```bash
cd web
npm run dev
```

**Access:** http://localhost:3000

**Features:**
- Multiplex network visualization
- Service status cards
- Bot profiles
- Landscape explorer

---

## Optional Services

### 🎨 ComfyUI (Image Generation)

Local AI image generation using Stable Diffusion and other models.

**Installation:**
```bash
# Clone ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI.git ~/ComfyUI
cd ~/ComfyUI

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip3 install -r requirements.txt
```

**Configure:**
```bash
# Add to .env
COMFYUI_PATH=/path/to/ComfyUI
```

**Running:**
```bash
cd $COMFYUI_PATH
source .venv/bin/activate
python3 main.py

# Access at http://localhost:8188
```

**GPU Requirements:**

| GPU | SD 1.5 | SDXL | SD 3.x / Flux |
|-----|--------|------|---------------|
| RTX 2060 (6GB) | ✅ Great | ⚠️ Use `--lowvram` | ❌ Too large |
| RTX 3060 (12GB) | ✅ Perfect | ✅ Great | ⚠️ Possible with optimizations |
| RTX 4090 (24GB) | ✅ Perfect | ✅ Perfect | ✅ Great |

**For low VRAM:**
```bash
python3 main.py --lowvram
```

**Integration:**
- Anya (creative director) uses ComfyUI for image generation
- Accessible via Telegram: `/anya generate a gothic cyberpunk garden`

---

### 🦙 Ollama (Local LLM Runtime)

Run open-source language models locally.

**Installation:**
```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh

# macOS
brew install ollama
```

**Running:**
```bash
ollama serve
```

**Pull models:**
```bash
ollama pull llama3.2
ollama pull mistral
ollama pull codellama
```

**Configure in Dome:**
1. Open http://localhost:8080
2. Settings → Connections
3. Add Ollama endpoint: `http://localhost:11434`

**Use cases:**
- Local inference (no API costs)
- Offline operation
- Privacy-sensitive tasks
- Code completion (CodeLlama)

---

## Network Access

### Local Network Access

Access services from other devices on your local network (phone, tablet, laptop):

**1. Find your local IP:**
```bash
hostname -I
# Example output: 192.168.1.100
```

**2. Access services:**
- Dome: `http://192.168.1.100:8080`
- Web Interface: `http://192.168.1.100:3000`
- ComfyUI: `http://192.168.1.100:8188`

**3. Configure firewall (if needed):**
```bash
# Allow ports
sudo ufw allow 8080/tcp
sudo ufw allow 3000/tcp
sudo ufw allow 8188/tcp
```

---

### Public Access (Temporary Tunnels)

Expose services to the internet temporarily via tunnels.

**Option 1: ssh.localhost.run (Quick)**
```bash
# Expose port 8080 (Dome)
ssh -R 80:localhost:8080 ssh.localhost.run

# You'll get a public URL like: https://random-name.localhost.run
```

**Option 2: Cloudflare Tunnel (Permanent)**
```bash
# Install cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/

# Start quick tunnel
cloudflared tunnel --url http://localhost:8080

# For permanent tunnels with custom domains, see Cloudflare Zero Trust docs
```

**Security Notes:**
- ⚠️ Tunnels expose services to the internet
- ✅ Use authentication (Cloudflare Access recommended)
- ✅ HTTPS is automatic with tunnels
- ⚠️ Quick tunnels are temporary and URLs change
- See [SSH_ACCESS.md](./SSH_ACCESS.md) for secure remote access

---

### Cloudflare Tunnel (Production Setup)

For permanent public access with authentication:

**1. Create Cloudflare account and add domain**

**2. Create tunnel:**
```bash
cloudflared tunnel create terrarium
```

**3. Configure services (`~/.cloudflared/config.yml`):**
```yaml
tunnel: <tunnel-id>
credentials-file: /home/$USER/.cloudflared/<tunnel-id>.json

ingress:
  # Dome (with Cloudflare Access authentication)
  - hostname: dome.yourdomain.com
    service: http://localhost:8080
    
  # Web interface
  - hostname: terrarium.yourdomain.com
    service: http://localhost:3000
    
  # Catch-all
  - service: http_status:404
```

**4. Route DNS:**
```bash
cloudflared tunnel route dns terrarium dome.yourdomain.com
cloudflared tunnel route dns terrarium terrarium.yourdomain.com
```

**5. Run tunnel:**
```bash
cloudflared tunnel run terrarium
```

**6. Add authentication (recommended):**
- Go to Cloudflare Zero Trust dashboard
- Create Access application
- Require email authentication
- See [SECURE_ACCESS.md](./SECURE_ACCESS.md) for details

---

## Service Management

### Starting Services

**All at once:**
```bash
./dev up
```

**Individual services:**
```bash
./dev up dome      # Just Open WebUI
./dev up portal    # Just Telegram
./dev up engine    # Just scheduler
```

### Stopping Services

```bash
./dev down         # Stop all
./dev stop dome    # Stop specific service
```

### Restarting

```bash
./dev restart dome   # Restart specific service
./dev down && ./dev up  # Restart everything
```

### Checking Status

```bash
./dev status       # Show all services
```

### Viewing Logs

```bash
# Attach to service (opens tmux session)
./dev attach dome

# Detach: Ctrl+B then D
```

---

## Performance Tuning

### GPU Optimization

**ComfyUI memory management:**
```bash
# Low VRAM (< 8GB)
python3 main.py --lowvram

# Very low VRAM (< 6GB)
python3 main.py --lowvram --novram
```

### Python Performance

**Use uvloop for async performance:**
```bash
pip3 install uvloop
```

**Multi-threading for scheduler:**
```bash
# Already optimized in terrarium scheduler
# Uses Python's asyncio for concurrent task execution
```

---

## Monitoring

### Service Health

```bash
# Check if services are responding
curl http://localhost:8080/health  # Dome
curl http://localhost:3000         # Web interface
```

### Resource Usage

```bash
# CPU and memory per service
htop

# GPU usage (if NVIDIA)
nvidia-smi

# Watch GPU continuously
watch -n 1 nvidia-smi
```

### Logs

**Dome (Open WebUI):**
- Check browser console (F12)
- Server logs in tmux: `./dev attach dome`

**Portal (Telegram):**
- Logs in tmux: `./dev attach portal`

**Engine (Scheduler):**
- Logs in tmux: `./dev attach engine`
- Visual feedback shows task execution in real-time

---

## Troubleshooting

### Port Conflicts

```bash
# Find what's using a port
lsof -i :8080

# Kill process
kill -9 <PID>
```

### Service Won't Start

```bash
# Check if dependencies are installed
pip3 list | grep <package>

# Reinstall dependencies
pip3 install -r requirements.txt --force-reinstall
```

### GPU Out of Memory

```bash
# Use lower VRAM mode
python3 main.py --lowvram

# Use smaller models
# SD 1.5 instead of SDXL
```

### Telegram Bot Not Responding

1. Check token in `.env`
2. Verify bot is running: `./dev status`
3. Check Telegram bot settings with @BotFather
4. Restart portal: `./dev restart portal`

---

## Next Steps

- [SETUP.md](./SETUP.md) - Installation and configuration
- [SSH_ACCESS.md](./SSH_ACCESS.md) - Remote access setup
- [SECURE_ACCESS.md](./SECURE_ACCESS.md) - Authentication and security
- [ARCHITECTURE.md](../ARCHITECTURE.md) - Multi-landscape design
