# Adding Home Button to Fern and Jarvis

To add the Terrarium home button to Fern and Jarvis sites:

## Option 1: Copy the Component

1. Copy `HomeButton.tsx` and `HomeButton.module.css` to your Fern/Jarvis project
2. Import and add to your layout or main page:

```tsx
import HomeButton from '@/components/navigation/HomeButton';

export default function Layout() {
  return (
    <>
      <HomeButton />
      {/* rest of your content */}
    </>
  );
}
```

## Option 2: Simple HTML/CSS (if not using React)

Add this to your HTML:

```html
<a href="https://mutatedterrarium.com" class="terrarium-home" title="Return to Terrarium">
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
    <polyline points="9 22 9 12 15 12 15 22" />
  </svg>
  <span>terrarium</span>
</a>

<style>
.terrarium-home {
  position: fixed;
  top: 1.5rem;
  left: 2rem;
  z-index: 1000;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.25rem;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 400;
  letter-spacing: 0.05em;
  transition: all 0.3s ease;
  text-transform: lowercase;
}

.terrarium-home:hover {
  background: rgba(0, 0, 0, 0.95);
  border-color: #EBFA1D;
  color: #EBFA1D;
  transform: translateY(-2px);
}
</style>
```

## Positioning

The button is positioned in the top-left corner. If you need it elsewhere, adjust the `top` and `left` CSS properties.
