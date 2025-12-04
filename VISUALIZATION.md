# 🌿 Terrarium 3D Visualization

## Overview

The Terrarium 3D Visualization is an interactive, real-time 3D representation of your AI ecosystem. It displays all your bots, services, and their activities in a stunning cyberpunk-organic glass dome environment.

## Quick Start

```bash
# Navigate to the visualization directory
cd terrarium-viz

# Launch (will auto-install dependencies if needed)
./start.sh

# Or manually
npm install
npm run dev
```

The visualization will open automatically at `http://localhost:3000`

## What You'll See

### 🤖 AI Bots
Represented as glowing spheres with orbit rings, arranged in a circle inside the dome:
- **Cassia** 🌅 - Golden morning light (daily planning)
- **Sage** 🧙 - Purple wisdom aura (strategic thinking)
- **Freya** 💪 - Green energy (health & fitness)
- **Nigella** 🍝 - Warm terracotta (culinary guide)
- **Nyx** 🚀 - Electric blue (tech futurist)
- **Anya** 🎨 - Rainbow spectrum (creative director)
- **Casper** 🤖 - Teal glow (Telegram concierge)
- **Pepper** ⚡ - Pink sparkle (ADHD assistant)
- **Luci** 🔮 - Mysterious violet

### ⚙️ Services
Represented as pillars with energy rings at the base:
- **Dome** 🌐 - Open WebUI
- **Engine** ⚙️ - Scheduler
- **Portal** 📱 - Telegram Bot
- **Bridge** 🌉 - MCP Bridge
- **Archive** 📚 - Document Archive

### ✨ Visual Features
- **Glass Dome** - Translucent protective sphere
- **Energy Rings** - Rotating rings showing data flow
- **Particles** - Floating data streams
- **Dynamic Lighting** - Ambient and accent lights
- **Real-time Status** - Active entities pulse and glow

## Controls

### Mouse/Trackpad
- **Left Click + Drag** - Rotate camera around terrarium
- **Right Click + Drag** - Pan camera position
- **Scroll** - Zoom in/out

### UI Buttons
- **Toggle Bots** - Show/hide AI bot entities
- **Toggle Services** - Show/hide service pillars
- **Toggle Particles** - Show/hide particle effects
- **Reset View** - Return camera to default position

### Keyboard Shortcuts
- **Esc** - Release pointer lock (if captured)

## Features

### Status Indicators
- **Active** - Bright glow, pulsing animation
- **Inactive** - Dim glow, static
- **Unknown** - Gray, no animation

### Activity Feed
Bottom-left panel shows recent activities:
- Bot actions
- Service events
- Scheduled tasks
- System messages

### Status Panel
Bottom-right panel shows real-time health:
- Service status (Dome, Engine, etc.)
- Bot availability
- Connection status

## Real-time Integration

The visualization can connect to your actual Terrarium environment:

### Option 1: Simulated Mode (Default)
No setup needed - visualization generates realistic simulated data.

### Option 2: Live Mode
Connect to your running Terrarium services:

```bash
# Terminal 1: Start your Terrarium services
dev up

# Terminal 2: Start the status monitor
cd terrarium-viz
npm run server

# Terminal 3: Start the visualization
npm run dev
```

The visualization will automatically detect and connect to the status server.

## Customization

### Change Colors
Edit colors in `src/core/TerrariumScene.ts`:

```typescript
const botConfigs = [
  { name: 'Cassia', emoji: '🌅', color: 0xffa500, position: 0 },
  // Change the hex color ^^^^^^^
];
```

### Add New Bots
Add to the `botConfigs` array in `TerrariumScene.ts`:

```typescript
{ name: 'NewBot', emoji: '🆕', color: 0xff00ff, position: 9 }
```

### Adjust Camera
Modify starting position in `TerrariumScene.ts`:

```typescript
this.camera.position.set(0, 8, 15); // x, y, z
```

## Performance

### Recommended System
- Modern GPU (dedicated graphics preferred)
- 4GB RAM minimum
- WebGL 2.0 support
- Chrome/Firefox/Edge (latest versions)

### Performance Tips
If experiencing lag:
1. Disable particles (✨ Toggle Particles button)
2. Reduce window size
3. Close other browser tabs
4. Update graphics drivers

### FPS Target
- **60 FPS** on modern hardware
- **30+ FPS** on integrated graphics
- Automatically adjusts quality based on performance

## Architecture

Built with:
- **Three.js** - 3D rendering
- **TypeScript** - Type-safe code
- **Vite** - Fast development
- **GSAP** - Smooth animations
- **Express** - Status API (optional)

## Development

### File Structure
```
terrarium-viz/
├── src/
│   ├── main.ts                   # Entry point
│   ├── core/
│   │   └── TerrariumScene.ts     # Main scene
│   ├── entities/
│   │   ├── BotEntity.ts          # Bot visuals
│   │   ├── ServiceEntity.ts      # Service visuals
│   │   └── TerraDome.ts          # Dome structure
│   ├── systems/
│   │   ├── ParticleSystem.ts     # Particle effects
│   │   └── StatusMonitor.ts      # Status polling
│   └── ui/
│       └── UIController.ts       # UI controls
├── server/
│   └── status-monitor.js         # Backend API
└── index.html                    # HTML template
```

### Build for Production
```bash
npm run build
```

Output in `dist/` - deploy to any static host.

## Troubleshooting

### Blank/Black Screen
- Check browser console for errors
- Verify WebGL support: `chrome://gpu`
- Try different browser
- Update graphics drivers

### Slow Performance
- Disable particles
- Reduce window size
- Close other applications
- Check GPU utilization

### Status Not Updating
- Verify services are running: `dev status`
- Check status server: `npm run server`
- Look at browser console for API errors
- Ensure port 3001 is not blocked

### Installation Errors
```bash
rm -rf node_modules package-lock.json
npm install
```

## Future Enhancements

Potential additions:
- [ ] Click on bots to see detailed info
- [ ] Historical activity timeline
- [ ] VR/AR mode support
- [ ] Export visualization as video
- [ ] Custom themes (dark/light)
- [ ] Sound effects for events
- [ ] Network topology view
- [ ] Performance metrics overlay
- [ ] Mobile-responsive controls

## Tips

1. **Best View**: Position camera at 45° angle for optimal perspective
2. **Performance**: Disable particles if needed, they're resource-intensive
3. **Screenshots**: Press F12 → Console → `document.querySelector('canvas').toDataURL()`
4. **Fullscreen**: F11 for immersive experience
5. **Development**: Hot reload enabled - changes reflect immediately

---

Enjoy exploring your AI ecosystem in 3D! 🌿✨
