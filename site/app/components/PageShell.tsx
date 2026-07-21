import Nav from "./Nav";
import Hero from "./Hero";
import HowItWorks from "./HowItWorks";
import ValueProps from "./ValueProps";
import Compare from "./Compare";
import Footer from "./Footer";

/* One page, two graph modes. Only the hero's GraphField behaviour differs. */
export default function PageShell({ mode }: { mode: "ambient" | "interactive" }) {
  return (
    <>
      <Nav mode={mode} />
      <main>
        <Hero mode={mode} />
        <HowItWorks />
        <ValueProps />
        <Compare />
      </main>
      <Footer />
    </>
  );
}
