import Hero from "./components/Hero";
import PromiseStrip from "./components/PromiseStrip";
import ContextTax from "./components/ContextTax";
import TokenTax from "./components/TokenTax";
import Values from "./components/Values";
import Compare from "./components/Compare";
import Footer from "./components/Footer";

/**
 * Final landing — assembled from locked screenshot cuts.
 */
export default function Home() {
  return (
    <>
      <main>
        <Hero />
        <PromiseStrip />
        <ContextTax />
        <TokenTax />
        <Values />
        <Compare />
      </main>
      <Footer />
    </>
  );
}
