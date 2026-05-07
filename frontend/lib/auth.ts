import { getServerSession } from "next-auth";
import { authOptions } from "@/app/api/auth/[...nextauth]/route";

/**
 * Get server session - should be used in server components only
 * This ensures secure session retrieval on the server side
 */
export async function getCurrentSession() {
  try {
    const session = await getServerSession(authOptions);
    return session;
  } catch (error) {
    console.error("Error retrieving session:", error);
    return null;
  }
}

/**
 * Check if user is authenticated
 */
export async function isAuthenticated(): Promise<boolean> {
  const session = await getCurrentSession();
  return !!session?.user;
}

/**
 * Get authenticated user
 */
export async function getAuthenticatedUser() {
  const session = await getCurrentSession();
  return session?.user || null;
}

/**
 * Save OAuth user to backend database
 * Called after successful OAuth login
 * Syncs OAuth user data with our Neon database
 */
export async function saveOAuthUserToDatabase(user: {
  id?: string;
  name?: string | null;
  email?: string | null;
  image?: string | null;
  provider?: string;
}) {
  try {
    // Validate required fields
    if (!user?.email) {
      console.warn("Cannot save user: missing email");
      return null;
    }

    if (!user?.provider) {
      console.warn("Cannot save user: missing provider");
      return null;
    }

    const apiUrl = process.env.NEXT_PUBLIC_API_URL;
    if (!apiUrl) {
      console.error("NEXT_PUBLIC_API_URL not configured");
      return null;
    }

    const response = await fetch(`${apiUrl}/auth/oauth/upsert`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: user.email,
        name: user.name || null,
        provider: user.provider.toLowerCase(),
        provider_id: user.id,
        image: user.image || null,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error(
        "Failed to save user:",
        response.status,
        errorData?.detail || "Unknown error"
      );
      return null;
    }

    const result = await response.json();
    console.log("User saved to database:", result.user_id);
    return result;
  } catch (error) {
    console.error("Error saving user to database:", error);
    return null;
  }
}
