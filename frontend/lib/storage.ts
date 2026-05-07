/**
 * Storage utilities for client-side state management
 */

/**
 * Get item from localStorage with error handling
 */
export function getFromStorage(key: string, defaultValue?: unknown): unknown {
  try {
    if (typeof window === "undefined") return defaultValue;
    const item = window.localStorage.getItem(key);
    return item ? JSON.parse(item) : defaultValue;
  } catch (error) {
    console.error(`Error reading from localStorage (key: ${key}):`, error);
    return defaultValue;
  }
}

/**
 * Set item in localStorage with error handling
 */
export function setToStorage(key: string, value: unknown): boolean {
  try {
    if (typeof window === "undefined") return false;
    window.localStorage.setItem(key, JSON.stringify(value));
    return true;
  } catch (error) {
    console.error(`Error writing to localStorage (key: ${key}):`, error);
    return false;
  }
}

/**
 * Remove item from localStorage
 */
export function removeFromStorage(key: string): boolean {
  try {
    if (typeof window === "undefined") return false;
    window.localStorage.removeItem(key);
    return true;
  } catch (error) {
    console.error(`Error removing from localStorage (key: ${key}):`, error);
    return false;
  }
}

/**
 * Clear all localStorage
 */
export function clearStorage(): boolean {
  try {
    if (typeof window === "undefined") return false;
    window.localStorage.clear();
    return true;
  } catch (error) {
    console.error("Error clearing localStorage:", error);
    return false;
  }
}

/**
 * Storage keys for auth system
 */
export const STORAGE_KEYS = {
  AUTH_REDIRECT: "auth_redirect_url",
  LAST_AUTH_PROVIDER: "last_auth_provider",
} as const;
