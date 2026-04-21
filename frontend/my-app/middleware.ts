import { auth } from "@/auth";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const PROTECTED = ["/dashboard", "/research"];
const AUTH_ONLY = ["/login", "/signup"];

export default auth((req: NextRequest & { auth: Awaited<ReturnType<typeof auth>> }) => {
  const { pathname } = req.nextUrl;
  const isLoggedIn = !!req.auth?.user;

  const isProtected = PROTECTED.some((p) => pathname.startsWith(p));
  const isAuthOnly = AUTH_ONLY.some((p) => pathname.startsWith(p));

  // Unauthenticated user hitting a protected page → redirect to login
  if (isProtected && !isLoggedIn) {
    const loginUrl = new URL("/login", req.url);
    loginUrl.searchParams.set("callbackUrl", pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Already-logged-in user hitting auth pages → send to dashboard
  if (isAuthOnly && isLoggedIn) {
    return NextResponse.redirect(new URL("/dashboard", req.url));
  }

  return NextResponse.next();
});

export const config = {
  // Run on all paths except static assets and Next.js internals
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};