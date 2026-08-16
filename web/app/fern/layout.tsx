import { Metadata } from "next";

export const metadata: Metadata = {
  title: "FERN Network - Fractal Towns for the Northern Shield",
  description:
    "FERN: A fractal town platform for the northern shield. 20 MW servers heat homes, 10⁶ agents run the loop, robots take the dark, and 2,500 humans just live. The towns are the leaflets.",
  keywords: [
    "FERN",
    "fractal towns",
    "northern shield",
    "Arctic communities",
    "data center heating",
    "sustainable infrastructure",
    "autonomous systems",
    "Indigenous partnerships",
    "renewable energy",
    "terrarium ecosystem",
  ],
  authors: [{ name: "Terrarium Project" }],
  openGraph: {
    title: "FERN Network - Fractal Towns for the Northern Shield",
    description:
      "FERN: 20 MW servers heat the homes. 10⁶ agents run the loop. Robots take the dark. 2,500 humans just live.",
    type: "website",
    url: "https://fern.mutatedterrarium.com",
    siteName: "FERN Network",
    images: [
      {
        url: "/api/og?title=FERN&subtitle=fractal%20towns%20for%20the%20northern%20shield",
        width: 1200,
        height: 630,
        alt: "FERN Network - Fractal Towns for the Northern Shield",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "FERN Network - Fractal Towns for the Northern Shield",
    description:
      "FERN: 20 MW servers heat the homes. 10⁶ agents run the loop. Robots take the dark. 2,500 humans just live.",
    images: [
      "/api/og?title=FERN&subtitle=fractal%20towns%20for%20the%20northern%20shield",
    ],
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function FernLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
