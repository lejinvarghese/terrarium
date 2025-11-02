# Terrarium
This is the terrarium where we live and grow our home. We have plants, animals, bots, and more! Some are digital, some are physical. We explore the intersection of technology and nature, and help look after our little ecosystem. We strive for mutual health and flourishing.


## Systems

### Open WebUI
Human friendly interface for models.

### ComfyUI
Generate art using local models or Runware models.

```bash
cd /home/starscream/_projects/ComfyUI
source .venv/bin/activate
python main.py
```

**GPU Specs:** NVIDIA GeForce RTX 2060 (6GB VRAM)

**Recommended Checkpoint Sizes:**
- ✅ **SD 1.5 models** (~2-4GB) - Best performance, room for LoRAs and ControlNet
- ✅ **SD 2.1 models** (~5GB) - Runs well
- ⚠️ **SDXL models** (~6-7GB) - Possible with optimizations (use `--lowvram` or `--medvram` flags)
- ❌ **SD 3.x** (8-10GB) or **Flux** (12GB+) - Too large for 6GB VRAM

**For SDXL, launch with optimizations:**
```bash
cd /home/starscream/_projects/ComfyUI
source .venv/bin/activate
python main.py --lowvram  # or --medvram for balance
```


### Ollama
Run local models via Ollama.


### Expose ports across network
We need to be able to access these services from inside our local network. 

```bash
ssh -R 80:localhost:8080 ssh.localhost.run
```

## Port Access

```bash
hostname -I
USERNAME=($whoami)
ssh USERNAME@ADDRESS
``` 