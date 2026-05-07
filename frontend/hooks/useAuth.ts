"use client";

import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useEffect, useCallback } from "react";
import type { Session } from "next-auth";

interface UseAuthOptions {
  redirectTo?: string;
  redirectIfFound?: boolean;
}

/**
 * Custom hook for client-side authentication
 * Provides session data and common auth operations
 */
export function useAuth(options: UseAuthOptions = {}) {
  const { data: session, status } = useSession();
  const router = useRouter();
  const { redirectTo = "/auth/signin", redirectIfFound = false } = options;

  const isAuthenticated = status === "authenticated" && !!session?.user;
  const isLoading = status === "loading";
  const isUnauthenticated = status === "unauthenticated";

  // Handle redirects based on auth status
  useEffect(() => {
    if (isLoading) return;

    if (isUnauthenticated && !redirectIfFound) {
      router.push(redirectTo);
    } else if (isAuthenticated && redirectIfFound) {
      router.push(redirectTo);
    }
  }, [isLoading, isUnauthenticated, isAuthenticated, redirectIfFound, redirectTo, router]);

  const user = useCallback((): Session["user"] | undefined => {
    return session?.user;
  }, [session]);

  return {
    session,
    user: user(),
    status,
    isAuthenticated,
    isLoading,
    isUnauthenticated,
  };
}
