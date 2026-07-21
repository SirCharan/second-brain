import Nav from "./components/Nav";
import Hero from "./components/Hero";
import FilmStrip from "./components/FilmStrip";
import Why from "./components/Why";
import Install from "./components/Install";
import Footer from "./components/Footer";

export default function Home() {
  return (
    <main className="relative flex min-h-full flex-col">
      <Nav />
      <Hero />
      <FilmStrip />
      <Why />
      <Install />
      <Footer />
    </main>
  );
}
