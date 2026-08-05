import { NextResponse } from "next/server";

/** irm charandeepkapoor.com/second-brain/install.ps1 | iex
 *  → the real script on GitHub main. basePath mounts this at /second-brain/install.ps1. */
export async function GET() {
  return NextResponse.redirect(
    "https://raw.githubusercontent.com/SirCharan/second-brain/main/install.ps1",
    307,
  );
}
