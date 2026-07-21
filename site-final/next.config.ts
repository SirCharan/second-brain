import type { NextConfig } from "next";

// Served as a Next.js Multi-Zone under charandeepkapoor.com/second-brain.
// basePath mounts every route + asset under /second-brain so the parent zone
// (ck-dot-com) can rewrite to it without /_next asset collisions. The standalone
// alias second-brain-final-psi.vercel.app/second-brain works too.
const nextConfig: NextConfig = {
  basePath: "/second-brain",
};

export default nextConfig;
