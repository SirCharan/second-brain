import Nav from "./components/Nav";
import Hero from "./components/Hero";
import HowItWorks from "./components/HowItWorks";
import ValueProps from "./components/ValueProps";
import Compare from "./components/Compare";
import Footer from "./components/Footer";

export default function Page() {
  return (
    <>
      <Nav />
      <main>
        <Hero />
        <HowItWorks />
        <ValueProps />
        <Compare />
      </main>
      <Footer />
    </>
  );
}
