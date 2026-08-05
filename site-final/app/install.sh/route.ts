import { NextResponse } from "next/server";

/** curl -fsSL charandeepkapoor.com/second-brain/install.sh | bash
 *  → the real script on GitHub main. basePath mounts this at /second-brain/install.sh. */
export async function GET() {
  return NextResponse.redirect(
    "https://raw.githubusercontent.com/SirCharan/second-brain/main/install.sh",
    307,
  );
}
