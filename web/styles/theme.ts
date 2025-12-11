import { createAppTheme } from '@arwes/react';

export const terrariumTheme = createAppTheme({
  settings: {
    hue: 180, // Cyan-based
    fontFamily: '"Inter", system-ui, sans-serif',
    fontFamilyCode: '"JetBrains Mono", monospace',
  },
  colors: {
    primary: {
      main: [180, 100, 50], // Cyan #00FFF2
      dark: [180, 100, 35],
      light: [180, 100, 65],
    },
    secondary: {
      main: [300, 100, 50], // Magenta #FF00FF
      dark: [300, 100, 35],
      light: [300, 100, 65],
    },
    accent: {
      main: [62, 98, 56], // Neon Yellow #EBFA1D
      dark: [62, 98, 40],
      light: [62, 98, 70],
    },
  },
});

export const colors = {
  primary: '#00FFF2',
  secondary: '#FF00FF',
  tertiary: '#EBFA1D',
  background: '#000814',
  surface: '#0A1929',
  gridLines: '#1A2332',
  textPrimary: '#E0E0E0',
  textSecondary: '#8F9BB3',
  textHeading: '#FFFFFF',
  textAccent: '#00FFF2',
  statusOnline: '#00FF88',
  statusOffline: '#FF3366',
  statusConfiguring: '#FFB800',
  accent: '#00D9FF',
};

export const fonts = {
  heading: '"Inter", system-ui, sans-serif',
  body: '"Inter", system-ui, sans-serif',
  mono: '"JetBrains Mono", monospace',
};

export const animations = {
  duration: {
    enter: 0.3,
    exit: 0.2,
    stagger: 0.05,
  },
  easing: {
    default: 'cubic-bezier(0.4, 0, 0.2, 1)',
    smooth: 'cubic-bezier(0.25, 0.1, 0.25, 1)',
  },
};
