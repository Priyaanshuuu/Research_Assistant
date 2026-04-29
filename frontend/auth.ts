import NextAuth from "next-auth";
import type { Session, User, Account } from "next-auth";
import type { JWT } from "next-auth/jwt";
import Google from "next-auth/providers/google";
import Credentials from "next-auth/providers/credentials";

const BACKEND = process.env.BACKEND_URL ?? "http://localhost:8000";

export const config = {
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID ?? "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET ?? "",
    }),
    Credentials({
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) return null;
        try {
          const res = await fetch(`${BACKEND}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              email: credentials.email,
              password: credentials.password,
            }),
          });
          if (!res.ok) return null;
          const data = await res.json();
          return {
            id: data.user_id,
            email: data.email,
            name: data.name ?? null,
            accessToken: data.access_token,
          };
        } catch (err) {
          console.error("[auth] Credentials authorize error:", err);
          return null;
        }
      },
    }),
  ],

  callbacks: {
    async signIn({ user, account }: { user: User; account: Account | null }) {
      if (account?.provider === "google") {
        try {
          const res = await fetch(`${BACKEND}/auth/oauth/upsert`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              email: user.email,
              name: user.name ?? null,
              provider: "google",
              provider_id: account.providerAccountId,
            }),
          });
          if (!res.ok) return false;
          const data = await res.json();
          user.id = data.user_id;
          user.accessToken = data.access_token;
        } catch (err) {
          console.error("[auth] OAuth upsert error:", err);
          return false;
        }
      }
      return true;
    },

    async jwt({ token, user }: { token: JWT; user: User }) {
      if (user) {
        token.userId = user.id as string;
        token.accessToken = user.accessToken as string;
      }
      return token;
    },
    async session({ session, token }: { session: Session; token: JWT }) {
      session.user.id = token.userId;
      session.accessToken = token.accessToken;
      return session;
    },
  },

  pages: {
    signIn: "/login",
    error: "/login",
  },

  session: { strategy: "jwt" as const },
};

export const { handlers, auth, signIn, signOut } = NextAuth(config);