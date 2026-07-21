import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";

const gambarino = localFont({
  src: "./fonts/Gambarino-Regular.woff2",
  variable: "--font-gambarino",
  display: "swap",
  weight: "400",
});

const SITE = "https://second-brain-final-psi.vercel.app";

export const metadata: Metadata = {
  title: "second-brain — the chat ends. the memory stays.",
  description:
    "Local-first AI memory as Markdown on your disk. Capture every session, recall in any model. Open source, no account.",
  metadataBase: new URL(SITE),
  openGraph: {
    title: "second-brain — the chat ends. the memory stays.",
    description:
      "Sessions write to files you own. Any model reads them back. Open source, no account.",
    url: SITE,
    siteName: "second-brain",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "second-brain — the chat ends. the memory stays.",
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
