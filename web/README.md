# Terrarium Web

A futuristic sci-fi web interface for the Terrarium AI ecosystem, inspired by NeoCultural Couture's design language.

## Overview

This is the web frontend for Terrarium, showcasing your self-hosted AI services with a stunning futuristic aesthetic. Built with Next.js 14, React 18, and the Arwes framework for sci-fi UI components.

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **UI Framework**: Arwes (Sci-Fi UI Components)
- **Styling**: CSS Modules + Emotion
- **Animations**: Framer Motion + CSS Animations
- **Fonts**: Inter (body) + JetBrains Mono (monospace)

## Features

- ✨ **Custom Cursor**: Interactive crosshair cursor with hover states
- 🎨 **Futuristic Design**: Cyberpunk-inspired UI with neon accents
- 🎭 **Service Cards**: Beautiful cards showcasing each AI service
- 🎬 **Smooth Animations**: Entrance, stagger, and hover animations
- 📱 **Responsive**: Works on desktop, tablet, and mobile
- ♿ **Accessible**: Respects reduced-motion preferences
- 🎵 **Sound Ready**: Infrastructure for sound effects (Arwes)

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

The dev server will be available at [http://localhost:3000](http://localhost:3000).

## Project Structure

```
web/
├── app/                    # Next.js app router pages
│   ├── layout.tsx         # Root layout with providers
│   └── page.tsx           # Home page
├── components/
│   ├── layout/            # Layout components (Nav, Footer, Cursor)
│   ├── sections/          # Page sections (Hero, Services, etc.)
│   ├── ui/                # Reusable UI components
│   └── effects/           # Visual effects (Particles, Grid)
├── styles/
│   ├── globals.css        # Global styles and resets
│   ├── animations.css     # Keyframe animations
│   └── theme.ts           # Theme configuration
├── data/
│   └── services.ts        # Service definitions and data
├── public/
│   └── assets/            # Static assets (sounds, images)
└── utils/                 # Utility functions
```

## Services

The site showcases these Terrarium services:

- **[001] Open WebUI** - Chat Interface Portal
- **[002] ComfyUI** - Creative Studio
- **[003] Ollama** - Model Runtime
- **[004] Letta AI** - Memory Engine
- **[005] SurrealDB** - Data Nexus

## Customization

### Colors

Edit `styles/theme.ts` to customize the color palette:

```typescript
export const colors = {
  primary: "#00FFF2", // Cyan
  secondary: "#FF00FF", // Magenta
  tertiary: "#EBFA1D", // Neon Yellow
  // ... more colors
};
```

### Services

Add or modify services in `data/services.ts`:

```typescript
export const services: Service[] = [
  {
    id: "myservice",
    name: "My Service",
    prefix: "[006]",
    tagline: "Service Tagline",
    description: "...",
    status: "online",
    color: "#00FFF2",
    // ...
  },
];
```

### Custom Cursor

The custom cursor can be disabled by commenting out the component in `app/layout.tsx`. It automatically hides on mobile devices and when users have `prefers-reduced-motion` enabled.

## Design Philosophy

The design follows these principles:

- **Sci-Fi Aesthetic**: Inspired by TRON, Star Citizen, and cyberpunk
- **Dark Theme**: Deep backgrounds with vibrant neon accents
- **Technical Feel**: Monospace fonts, grid patterns, technical prefixes
- **Smooth Animations**: Entrance effects, hover states, transitions
- **Accessibility**: Respects user preferences and provides alternatives

## Performance

- Lazy loading for heavy components
- Optimized fonts with `next/font`
- CSS Modules for scoped styles
- Code splitting by route
- WebP images with fallbacks

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Accessibility

- Keyboard navigation
- Screen reader friendly
- Respects `prefers-reduced-motion`
- WCAG AA color contrast
- Semantic HTML

## Future Enhancements

- [ ] Particle background effect
- [ ] Lottie animations
- [ ] Sound effects integration
- [ ] Service detail pages
- [ ] Real-time service status
- [ ] Data visualization
- [ ] Blog/news section

## License

Part of the Terrarium project. See main project for license information.

## Credits

- Design inspiration: [NeoCultural Couture](https://www.neoculturalcouture.com/)
- UI Framework: [Arwes](https://arwes.dev/)
- Built with ❤️ for the open source community
