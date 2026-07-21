import Hero from "./components/Hero";
import PromiseStrip from "./components/PromiseStrip";
import ContextTax from "./components/ContextTax";
import TokenTax from "./components/TokenTax";
import Values from "./components/Values";

/**
 * Final landing — assembled from locked screenshot cuts.
 * More sections as screenshots arrive.
 */
export default function Home() {
  return (
    <main>
      <Hero />
      <PromiseStrip />
      <ContextTax />
      <TokenTax />
      <Values />
    </main>
  );
}
