import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
//import { auth } from '@/auth'

const PROTECTED = ["/dashboard", "/research"]
const AUTH_ONLY = ["/login", "/signup"]

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl
  //const isLoggedIn = !!request.auth?.user

  const isProtected = PROTECTED.some((p) => pathname.startsWith(p))
  const isAuthOnly = AUTH_ONLY.some((p) => pathname.startsWith(p))

  if (isProtected && !isLoggedIn) {
    const loginUrl = new URL("/login", request.url)
    loginUrl.searchParams.set("callbackUrl", pathname)
    return NextResponse.redirect(loginUrl)
  }

  if (isAuthOnly && isLoggedIn) {
    return NextResponse.redirect(new URL("/dashboard", request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
}