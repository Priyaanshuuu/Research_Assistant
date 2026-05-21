import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function isPublicRoute(pathname: string, publicRoutes: readonly string[]): boolean {
  return publicRoutes.some(route => {
    // Exact match
    if (pathname === route) return true;
    // Prefix match for nested routes (e.g., /api/auth matches /api/auth/callback)
    if (route.includes("/api")) {
      return pathname.startsWith(route);
    }
    return false;
  });
}
export function isRouteProtected(pathname: string, protectedRoutes: readonly string[]): boolean {
  return protectedRoutes.some(route => {
    // Exact match
    if (pathname === route) return true;
    // Prefix match for nested routes (e.g., /dashboard matches /dashboard/...)
    return pathname.startsWith(route + "/");
  });
}

export function getInitials(name?: string | null): string {
  if (!name) return "U";
  const parts = name.trim().split(/\s+/);
  if (parts.length >= 2) {
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  }
  return name.slice(0, 2).toUpperCase();
}

export function formatUserName(name?: string | null): string {
  if (!name) return "User";
  return name.charAt(0).toUpperCase() + name.slice(1).toLowerCase();
}