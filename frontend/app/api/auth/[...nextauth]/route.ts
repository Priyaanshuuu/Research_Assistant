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
    async jwt({ token, user, account }) {
      if (user?.backendAccessToken) {
        token.backendAccessToken = user.backendAccessToken;
      }
      if (account) {
        token.provider = account.provider;
      }
      if (user) {
        token.name = user.name;
        token.email = user.email;
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
        session.user.name = token.name;
        session.user.email = token.email;
      }
      session.accessToken = token.backendAccessToken;
      return session;
    },
    async redirect({ baseUrl }) {
      // Always redirect to dashboard after sign in
      return `${baseUrl}/dashboard`;
    },

    async signIn({ user, account }) {
      try {
        if (!user?.email) return false;

        if (account?.provider) {
          try {
            const { saveOAuthUserToDatabase } = await import("@/lib/auth");

            const backendResult = await saveOAuthUserToDatabase({
              id: account.providerAccountId,
              name: user?.name,
              email: user?.email,
              image: user?.image,
              provider: account.provider,
            });

            if (backendResult?.access_token) {
              // Store backend JWT in user object so it goes into token
              user.backendAccessToken = backendResult.access_token;
              console.log("User successfully persisted to database");
            } else {
              console.warn(
                "User not persisted to database, but OAuth login allowed (graceful degradation)"
              );
            }
          } catch (err) {
            console.error("Error saving user to database:", err);
            // Graceful degradation: don't block OAuth login if database save fails
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