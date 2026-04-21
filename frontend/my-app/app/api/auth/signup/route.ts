import { NextRequest, NextResponse } from "next/server";

const BACKEND = process.env.BACKEND_URL ?? "http://localhost:8000";

// Proxies registration to FastAPI so the BACKEND_URL env var (server-only)
// is never exposed to the browser.
export async function POST(req: NextRequest): Promise<NextResponse> {
  try {
    const body = await req.json();

    const res = await fetch(`${BACKEND}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    const data = await res.json();

    if (!res.ok) {
      return NextResponse.json(
        { error: data.detail ?? "Registration failed" },
        { status: res.status }
      );
    }

    return NextResponse.json(data);
  } catch (err) {
    console.error("[signup route] Error:", err);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}