# 🌿 Terrarium 3D Visualization

An interactive 3D visualization of the Terrarium AI ecosystem, bringing your bots and services to life in a stunning cyberpunk-organic glass dome.

![Terrarium Viz](https://img.shields.io/badge/Three.js-0.160-blue) ![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue) ![Vite](https://img.shields.io/badge/Vite-5.0-purple)

## ✨ Features

### 🎨 Visual Design
- **Glass terrarium dome** - translucent sphere with energy rings, ground grid, ambient particles
- **9 AI bot entities** - glowing spheres with orbit rings, unique colors, floating animation, labels with emoji
- **5 core services** - infrastructure pillars with energy rings, icon sprites, entrance animations
- **Particle systems** - 500 floating particles + 5 spiral data streams
- **Dynamic lighting** - ambient, directional (sun), accent lights, per-entity point lights
- **Animations** - floating, pulsing, rotation, elastic entrance effects (GSAP)

### 🎮 Interactive Features
- **Orbit controls** - rotate (left drag), pan (right drag), zoom (scroll)
- **Toggle buttons** - show/hide bots, services, particles
- **Reset camera** - return to default view
- **Smooth interactions** - damped controls, inertial movement

### 📊 Status Monitoring
- **Real-time polling** - 5s intervals, checks tmux sessions & processes
- **Activity feed** - last 10 events, color-coded by type, relative timestamps
- **Status panel** - all entities with green/red/gray indicators
- **Visual feedback** - active entities glow brighter and pulse

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ (for development)
- npm or yarn

### Installation

```bash
# Navigate to the project
cd terrarium-viz

# Install dependencies
npm install

# Start development server
npm run dev
```

The visualization will open at `http://localhost:3000`

### Optional: Run Status Monitor

For real-time status updates from your actual Terrarium services:

```bash
# In a separate terminal
npm run server
```

This starts a backend server on port 3001 that monitors your tmux sessions and processes.

## 🎯 Usage

### Controls
- **Left Mouse**: Rotate camera
- **Right Mouse**: Pan camera
- **Scroll**: Zoom in/out
- **UI Buttons**: Toggle visibility, reset view

### Status Integration

The visualization can connect to your live Terrarium environment:

1. Make sure your Terrarium services are running (`dev up`)
2. Start the status monitor server (`npm run server`)
3. The visualization will automatically fetch and display real status

If the server isn't running, the visualization will use simulated data.

## 🏗️ Architecture

```
terrarium-viz/
├── src/
│   ├── main.ts              # Entry point
│   ├── core/
│   │   └── TerrariumScene.ts  # Main 3D scene
│   ├── entities/
│   │   ├── BotEntity.ts       # AI bot representations
│   │   ├── ServiceEntity.ts   # Service nodes
│   │   └── TerraDome.ts       # Glass dome
│   ├── systems/
│   │   ├── ParticleSystem.ts  # Particle effects
│   │   └── StatusMonitor.ts   # Status polling
│   └── ui/
│       └── UIController.ts    # UI interactions
├── server/
│   └── status-monitor.js    # Backend status API
├── index.html               # HTML template
├── package.json
└── vite.config.ts
```

## 🎨 Customization

### Adding New Bots

Edit `src/core/TerrariumScene.ts` and add to the `botConfigs` array:

```typescript
{ name: 'YourBot', emoji: '🤖', color: 0xff00ff, position: 9 }
```

### Changing Colors

Bot and service colors are defined in hex format (e.g., `0x00ff88`):
- Update in `TerrariumScene.ts` for initial creation
- Modify materials in `BotEntity.ts` or `ServiceEntity.ts` for effects

### Adjusting Camera

Edit camera position in `TerrariumScene.ts`:

```typescript
this.camera.position.set(x, y, z);
```

## 🔧 Development

### Build for Production

```bash
npm run build
```

Output will be in `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## 🌐 Deployment

### Static Hosting

The built application is a static site that can be deployed to:
- Netlify
- Vercel
- GitHub Pages
- Any static host

### With Backend

For live status monitoring, deploy both:
1. Frontend (static) to your preferred host
2. Backend (`server/status-monitor.js`) to a Node.js server

Update the status fetch URL in `StatusMonitor.ts` to point to your backend.

## 📝 Technical Details

### Technologies
- **Three.js** - 3D rendering engine
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool and dev server
- **GSAP** - Smooth animations
- **Express** - Backend status API

### Performance
- Optimized particle systems with instancing
- Efficient geometry reuse
- 60 FPS target on modern hardware
- Responsive to window resize

### Browser Support
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- WebGL 2.0 required

## 🐛 Troubleshooting

### "Module not found" errors
```bash
npm install
```

### Black screen on load
- Check browser console for errors
- Ensure WebGL is supported
- Try a different browser

### Status not updating
- Verify status server is running (`npm run server`)
- Check if Terrarium services are running (`dev status`)
- Look at network tab for API errors

## 🤝 Contributing

This visualization is part of the Terrarium project. Feel free to customize for your own ecosystem!

## 📄 License

Part of the Terrarium project - personal AI ecosystem orchestration.

---

Built with 💚 for the Terrarium AI ecosystem
