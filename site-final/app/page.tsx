import Nav from "./components/Nav";
import Hero from "./components/Hero";
import PromiseStrip from "./components/PromiseStrip";
import WorksWith from "./components/WorksWith";
import ContextTax from "./components/ContextTax";
import TokenTax from "./components/TokenTax";
import Values from "./components/Values";
import Compare from "./components/Compare";
import Footer from "./components/Footer";

/**
 * Final landing — assembled from locked screenshot cuts + polish pass.
 */
export default function Home() {
  return (
    <>
      <Nav />
      <main>
        <Hero />
        <PromiseStrip />
        <WorksWith />
        <ContextTax />
        <TokenTax />
        <Values />
        <Compare />
      </main>
      <Footer />
    </>
  );
}
