import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";

const gambarino = localFont({
  src: "./fonts/Gambarino-Regular.woff2",
  variable: "--font-gambarino",
  display: "swap",
  weight: "400",
});

export const metadata: Metadata = {
  title: "second-brain — the chat ends. the memory stays.",
  description:
    "Local-first AI memory as Markdown on your disk. Capture every session, recall in any model. Open source, no account.",
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
