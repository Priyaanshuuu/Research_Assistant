import { NextRequest, NextResponse } from "next/server";
import { PUBLIC_ROUTES, PROTECTED_ROUTES } from "@/lib/constants";
import { isPublicRoute, isRouteProtected } from "@/lib/utils";

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Check if current route is public
  const isPublic = isPublicRoute(pathname, PUBLIC_ROUTES);

  // Check if current route is protected
  const isProtected = isRouteProtected(pathname, PROTECTED_ROUTES);

  // Get session token from cookies
  const token = request.cookies.get("next-auth.session-token")?.value;

  // If the route is protected and no token exists, redirect to signin
  if (isProtected && !token) {
    const signInUrl = new URL("/auth/signin", request.url);
    signInUrl.searchParams.set("callbackUrl", pathname);
    return NextResponse.redirect(signInUrl);
  }

  // If the route is public and user is already authenticated, allow access
  // (they can stay on public pages even when logged in)
  if (isPublic) {
    return NextResponse.next();
  }

  // Allow other requests to proceed normally
  return NextResponse.next();
}

// Configure which routes the proxy should run on
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public (public folder)
     */
    "/((?!api|_next/static|_next/image|favicon.ico|public).*)",
  ],
};
