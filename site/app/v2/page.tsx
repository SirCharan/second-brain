import type { Metadata } from "next";
import Nav from "./components/Nav";
import Hero from "./components/Hero";
import PromiseStrip from "./components/PromiseStrip";
import HowItWorks from "./components/HowItWorks";
import Values from "./components/Values";
import Compare from "./components/Compare";
import Footer from "./components/Footer";

export const metadata: Metadata = {
  title: "second-brain — memory that outlives every chat",
  description:
    "Local-first AI memory as Markdown on your disk. Capture every session, recall in any model, never rent your brain again.",
  openGraph: {
    title: "second-brain — memory that outlives every chat",
    description:
      "Sessions write to files you own. Any model reads them back. Open source, no account.",
  },
};

export default function V2Page() {
  return (
    <>
      <Nav />
      <main>
        <Hero />
        <PromiseStrip />
        <HowItWorks />
        <Values />
        <Compare />
      </main>
      <Footer />
    </>
  );
}
