import NextAuth from "next-auth";
import type { NextAuthOptions } from "next-auth";
import GitHubProvider from "next-auth/providers/github";
import GoogleProvider from "next-auth/providers/google";
import "@/types/auth";

export const authOptions: NextAuthOptions = {
  providers: [
    GitHubProvider({
      clientId: process.env.GITHUB_ID || "",
      clientSecret: process.env.GITHUB_SECRET || "",
    }),
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID || "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || "",
    }),
  ],

  session: {
    strategy: "jwt",
    maxAge: 30 * 24 * 60 * 60, // 30 days
    updateAge: 24 * 60 * 60, // 24 hours
  },

  pages: {
    signIn: "/auth/signin",
    error: "/auth/error",
  },

  callbacks: {
    async jwt({ token, account, profile }) {
      if (account) {
        token.provider = account.provider;
        token.accessToken = account.access_token;
      }
      if (profile) {
        token.name = profile.name;
        token.email = profile.email;
      }
      return token;
    },

    /**
     * Session callback - called when session is retrieved
     * Used to add properties to the session object
     */
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.sub;
        session.user.provider = token.provider;
        session.user.name = token.name;
        session.user.email = token.email;
        //session.user.image = token.picture as string | null;
      }
      return session;
    },
    async redirect({ url, baseUrl }) {
      // Allow relative URLs
      if (url.startsWith("/")) {
        return `${baseUrl}${url}`;
      }
      // Allow same origin URLs
      if (new URL(url).origin === baseUrl) {
        return url;
      }
      // Default redirect to dashboard after sign in
      return `${baseUrl}/dashboard`;
    },

    async signIn({ user, account }) {
      try {
        if (!user?.email) {
          return false;
        }

        // For OAuth providers, save user to backend database
        if (account?.provider) {
          try {
            console.log(
              `OAuth signIn: ${account.provider} - ${user?.email}`
            );

            // Import function dynamically to avoid circular dependency
            const { saveOAuthUserToDatabase } = await import("@/lib/auth");

            const backendResult = await saveOAuthUserToDatabase({
              id: account.providerAccountId,
              name: user?.name,
              email: user?.email,
              image: user?.image,
              provider: account.provider,
            });

            if (!backendResult) {
              console.warn(
                "User not persisted to database, but OAuth login allowed (graceful degradation)"
              );
            } else {
              console.log("User successfully persisted to database");
            }
          } catch (err) {
            console.error(
              "Error saving user to database during OAuth signIn:",
              err
            );
            // Graceful degradation: don't block OAuth login if database save fails
            // User is still logged in via NextAuth even if backend persistence fails
          }
        }

        return true;
      } catch (error) {
        console.error("SignIn callback error:", error);
        return false;
      }
    },
  },

  events: {
    async signIn({ user, account }) {
      console.log(`User ${user?.email} signed in via ${account?.provider}`);
    },
    async signOut() {
      console.log("User signed out");
    },
  },

  secret: process.env.NEXTAUTH_SECRET,
};

const handler = NextAuth(authOptions);

export { handler as GET, handler as POST };