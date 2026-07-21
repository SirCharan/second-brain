import type { Metadata } from "next";
import localFont from "next/font/local";
import { IBM_Plex_Sans, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";

const display = localFont({
  src: "./fonts/Gambarino-Regular.woff2",
  variable: "--font-display",
  display: "swap",
  weight: "400",
});

const body = IBM_Plex_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-body",
  display: "swap",
});

const mono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "second-brain — memory that outlives the chat",
  description:
    "Local-first memory for AI assistants. Plain Markdown on your disk, recalled into any model. Open source.",
  openGraph: {
    title: "second-brain — memory that outlives the chat",
    description:
      "Local-first memory for AI assistants. Plain Markdown on your disk, recalled into any model.",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "second-brain",
    description: "Local-first memory for AI assistants. Own it. Switch models freely.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${display.variable} ${body.variable} ${mono.variable} h-full`}
    >
      <body className="min-h-full bg-bg text-fg antialiased">
        <div className="letterbox letterbox-top" aria-hidden />
        <div className="letterbox letterbox-bottom" aria-hidden />
        <div className="grain" aria-hidden />
        {children}
      </body>
    </html>
  );
}
