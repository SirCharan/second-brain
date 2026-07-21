import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";

const gambarino = localFont({
  src: "./fonts/Gambarino-Regular.woff2",
  variable: "--font-gambarino",
  display: "swap",
  weight: "400",
});

const SITE = "https://github.com/SirCharan/second-brain";

export const metadata: Metadata = {
  title: "second-brain — your memory, every model, your disk",
  description:
    "A local-first, file-based memory for AI assistants. Own it, switch models freely, never run out of context. Open source for Claude Code.",
  metadataBase: new URL("https://second-brain.dev"),
  openGraph: {
    title: "second-brain — your memory, every model, your disk",
    description:
      "Local-first, file-based AI memory. Own it, switch models freely, never compact a conversation again.",
    url: SITE,
    siteName: "second-brain",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "second-brain — your memory, every model, your disk",
    description: "Local-first, file-based AI memory. Own your mind; rent the model.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${gambarino.variable} h-full`}>
      <body className="min-h-full">{children}</body>
    </html>
  );
}
