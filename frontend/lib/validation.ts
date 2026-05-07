/**
 * Validation utilities for form inputs and auth
 */

/**
 * Validate email format
 */
export function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Validate required field
 */
export function validateRequired(value: string | null | undefined): boolean {
  return typeof value === "string" && value.trim().length > 0;
}

/**
 * Validate URL format
 */
export function validateUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

/**
 * Validate OAuth provider
 */
export function validateOAuthProvider(provider: string): boolean {
  const validProviders = ["github", "google"];
  return validProviders.includes(provider.toLowerCase());
}

/**
 * Sanitize string input
 */
export function sanitizeString(str: string | null | undefined): string {
  if (!str) return "";
  // Remove dangerous characters and trim
  return str
    .replace(/[<>]/g, "")
    .trim();
}

/**
 * Validate session token structure
 */
export function isValidSessionToken(token: string | null | undefined): boolean {
  if (!token) return false;
  // Basic validation - tokens should be strings
  return typeof token === "string" && token.length > 10;
}

/**
 * Validate callback URL
 */
export function isValidCallbackUrl(url: string): boolean {
  try {
    const urlObj = new URL(url, typeof window !== "undefined" ? window.location.origin : "http://localhost:3000");
    // Only allow same origin for security
    return urlObj.origin === (typeof window !== "undefined" ? window.location.origin : "http://localhost:3000");
  } catch {
    return false;
  }
}
