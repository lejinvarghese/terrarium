import type { Metadata } from "next";
import { JetBrains_Mono } from "next/font/google";
import Script from "next/script";
import "../styles/globals.css";
import "../styles/animations.css";
import CustomCursor from "@/components/layout/CustomCursor";
import Preloader from "@/components/layout/Preloader";
import AudioPlayer from "@/components/ui/AudioPlayer";

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains-mono",
});

export const metadata: Metadata = {
  title: "Terrarium | Cybernetic Swarm Intelligence",
  description:
    "A self-hosted habitat where cybernetic minds swarm, grow, and tend to your ecosystem. Step through the glass—where technology and life merge as one.",
  keywords: [
    "Cybernetic Minds",
    "Swarm Intelligence",
    "Self-hosted",
    "Digital Home",
    "Distributed AI",
    "Cyberpunk",
  ],
  authors: [{ name: "starscream" }],
  openGraph: {
    title: "Terrarium | Cybernetic Swarm Intelligence",
    description:
      "A digital home where cybernetic minds live as a collective swarm.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        {/* Google Tag Manager */}
        <Script
          id="gtm-script"
          strategy="afterInteractive"
          dangerouslySetInnerHTML={{
            __html: `(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-WD3647LK');`,
          }}
        />
        {/* Google Analytics */}
        <Script
          src="https://www.googletagmanager.com/gtag/js?id=G-3JPCD3VVSX"
          strategy="afterInteractive"
        />
        <Script
          id="gtag-init"
          strategy="afterInteractive"
          dangerouslySetInnerHTML={{
            __html: `
              window.dataLayer = window.dataLayer || [];
              function gtag(){dataLayer.push(arguments);}
              gtag('js', new Date());
              gtag('config', 'G-3JPCD3VVSX');
            `,
          }}
        />
      </head>
      <body className={jetbrainsMono.variable}>
        {/* Google Tag Manager (noscript) */}
        <noscript>
          <iframe
            src="https://www.googletagmanager.com/ns.html?id=GTM-WD3647LK"
            height="0"
            width="0"
            style={{ display: "none", visibility: "hidden" }}
          ></iframe>
        </noscript>
        <Preloader />
        <CustomCursor />
        <AudioPlayer autoPlay={true} volume={0.7} />
        {children}
      </body>
    </html>
  );
}
