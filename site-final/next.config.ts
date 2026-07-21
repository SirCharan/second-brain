import type { NextConfig } from "next";

// Served as a Next.js Multi-Zone under charandeepkapoor.com/second-brain.
// basePath mounts every route + asset under /second-brain so the parent zone
// can rewrite to it without asset collisions.
const nextConfig: NextConfig = {
  basePath: "/second-brain",
};

export default nextConfig;
