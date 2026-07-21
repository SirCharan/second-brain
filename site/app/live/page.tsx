import PageShell from "../components/PageShell";

export const metadata = {
  title: "second-brain — interactive graph",
  description:
    "The interactive Obsidian-style memory graph. Hover a node to light its pathways, drag it around. Local-first AI memory.",
};

export default function LivePage() {
  return <PageShell mode="interactive" />;
}
