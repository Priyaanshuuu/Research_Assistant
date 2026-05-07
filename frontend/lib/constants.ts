/**
 * Authentication routes
 */
export const AUTH_ROUTES = {
  SIGNIN: "/auth/signin",
  CALLBACK: "/api/auth/callback",
  SIGNOUT: "/api/auth/signout",
  ERROR: "/auth/error",
} as const;

/**
 * Public routes that don't require authentication
 */
export const PUBLIC_ROUTES = [
  "/",
  "/auth/signin",
  "/auth/error",
  "/api/auth",
  "/public",
] as const;

/**
 * Protected routes that require authentication
 */
export const PROTECTED_ROUTES = ["/dashboard"] as const;

/**
 * Error messages
 */
export const ERROR_MESSAGES = {
  MISSING_CREDENTIALS: "Missing authentication credentials",
  INVALID_SESSION: "Invalid or expired session",
  UNAUTHORIZED: "Unauthorized access",
  INTERNAL_ERROR: "An internal error occurred",
  OAUTH_ERROR: "OAuth authentication failed",
} as const;
