/**
 * Utility functions for authentication and common operations
 */

/**
 * Check if a route matches a pattern
 */
export function isRouteProtected(pathname: string, protectedRoutes: readonly string[]): boolean {
  return protectedRoutes.some((route) => {
    if (route.includes(":")) {
      // Handle dynamic routes like /dashboard/:id
      const pattern = route.replace(/:[^\s/]+/g, "[^/]+");
      return new RegExp(`^${pattern}$`).test(pathname);
    }
    return pathname === route || pathname.startsWith(route + "/");
  });
}

/**
 * Check if a route is public
 */
export function isPublicRoute(pathname: string, publicRoutes: readonly string[]): boolean {
  return publicRoutes.some((route) => {
    if (route.includes(":")) {
      const pattern = route.replace(/:[^\s/]+/g, "[^/]+");
      return new RegExp(`^${pattern}$`).test(pathname);
    }
    return pathname === route || pathname.startsWith(route + "/");
  });
}

/**
 * Get initials from a name
 */
export function getInitials(name: string | null | undefined): string {
  if (!name) return "?";
  return name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

/**
 * Format user display name
 */
export function formatUserName(name: string | null | undefined): string {
  if (!name) return "User";
  return name.charAt(0).toUpperCase() + name.slice(1).toLowerCase();
}
