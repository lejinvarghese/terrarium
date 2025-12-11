import type { Metadata } from 'next';
import { Inter, JetBrains_Mono } from 'next/font/google';
import '../styles/globals.css';
import '../styles/animations.css';
import CustomCursor from '@/components/layout/CustomCursor';
import Preloader from '@/components/layout/Preloader';
import AudioPlayer from '@/components/ui/AudioPlayer';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });
const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-jetbrains-mono'
});

export const metadata: Metadata = {
  title: 'Terrarium | AI Ecosystem',
  description: 'Where AI ecosystems thrive and innovation blooms. Your self-hosted AI infrastructure.',
  keywords: ['AI', 'Machine Learning', 'Open WebUI', 'ComfyUI', 'Ollama', 'Self-hosted'],
  authors: [{ name: 'Terrarium Team' }],
  openGraph: {
    title: 'Terrarium | AI Ecosystem',
    description: 'Where AI ecosystems thrive and innovation blooms',
    type: 'website',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${jetbrainsMono.variable}`}>
        <Preloader />
        <CustomCursor />
        <AudioPlayer />
        {children}
      </body>
    </html>
  );
}
