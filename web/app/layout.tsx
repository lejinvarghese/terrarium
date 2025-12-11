import type { Metadata } from 'next';
import { JetBrains_Mono } from 'next/font/google';
import '../styles/globals.css';
import '../styles/animations.css';
import CustomCursor from '@/components/layout/CustomCursor';
import Preloader from '@/components/layout/Preloader';
import AudioPlayer from '@/components/ui/AudioPlayer';

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-jetbrains-mono'
});

export const metadata: Metadata = {
  title: 'Terrarium | Cybernetic Swarm Intelligence',
  description: 'A self-hosted habitat where cybernetic minds swarm, grow, and tend to your ecosystem. Step through the glass—where technology and life merge as one.',
  keywords: ['Cybernetic Minds', 'Swarm Intelligence', 'Self-hosted', 'Digital Home', 'Distributed AI', 'Cyberpunk'],
  authors: [{ name: 'starscream' }],
  openGraph: {
    title: 'Terrarium | Cybernetic Swarm Intelligence',
    description: 'A digital home where cybernetic minds operate as a collective swarm.',
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
      <body className={jetbrainsMono.variable}>
        <Preloader />
        <CustomCursor />
        <AudioPlayer autoPlay={true} />
        {children}
      </body>
    </html>
  );
}
