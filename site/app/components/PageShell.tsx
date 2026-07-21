import Nav from "./Nav";
import Hero from "./Hero";
import WorksWith from "./WorksWith";
import HowItWorks from "./HowItWorks";
import ValueProps from "./ValueProps";
import CostSaver from "./CostSaver";
import Compare from "./Compare";
import Roadmap from "./Roadmap";
import Footer from "./Footer";

/* One page, two graph modes. Only the hero's GraphField behaviour differs. */
export default function PageShell({ mode }: { mode: "ambient" | "interactive" }) {
  return (
    <>
      <Nav mode={mode} />
      <main>
        <Hero mode={mode} />
        <WorksWith />
        <HowItWorks />
        <ValueProps />
        <CostSaver />
        <Compare />
        <Roadmap />
      </main>
      <Footer />
    </>
  );
}
