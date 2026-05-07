/**
 * Authentication documentation and setup guide
 * 
 * ## Overview
 * 
 * This authentication system uses NextAuth.js with OAuth 2.0 providers
 * (GitHub and Google) for secure user authentication.
 * 
 * ## Features
 * 
 * - OAuth 2.0 authentication with GitHub and Google
 * - JWT-based sessions for stateless auth
 * - Secure callback handling
 * - Automatic session refresh
 * - Protected routes with proxy.ts
 * - Server-side session retrieval
 * - Client-side session context
 * 
 * ## File Structure
 * 
 * ```
 * frontend/
 * ├── app/
 * │   ├── api/
 * │   │   └── auth/[...nextauth]/
 * │   │       └── route.ts          # NextAuth configuration
 * │   ├── auth/
 * │   │   ├── signin/
 * │   │   │   └── page.tsx          # Sign in page
 * │   │   └── error/
 * │   │       └── page.tsx          # Auth error page
 * │   ├── dashboard/
 * │   │   └── page.tsx              # Protected dashboard
 * │   ├── error.tsx                 # Error boundary
 * │   ├── global-error.tsx          # Global error boundary
 * │   ├── not-found.tsx             # 404 page
 * │   ├── layout.tsx                # Root layout with SessionProvider
 * │   ├── page.tsx                  # Landing page
 * │   └── providers.tsx             # SessionProvider wrapper
 * ├── lib/
 * │   ├── auth.ts                   # Server-side auth functions
 * │   ├── constants.ts              # Auth routes & constants
 * │   ├── env.ts                    # Environment variables
 * │   ├── utils.ts                  # Utility functions
 * │   └── validation.ts             # Validation utilities
 * ├── hooks/
 * │   └── useAuth.ts                # Custom auth hook
 * ├── types/
 * │   └── auth.ts                   # TypeScript types
 * ├── proxy.ts                      # Route protection
 * ├── next.config.ts                # Next.js config
 * └── .env.local                    # Environment variables
 * ```
 * 
 * ## Environment Variables
 * 
 * Required environment variables in .env.local:
 * 
 * ```
 * NEXTAUTH_SECRET=<64-char-random-string>
 * NEXTAUTH_URL=http://localhost:3000
 * 
 * # GitHub OAuth
 * GITHUB_ID=<github-oauth-app-id>
 * GITHUB_SECRET=<github-oauth-app-secret>
 * 
 * # Google OAuth
 * GOOGLE_CLIENT_ID=<google-oauth-client-id>
 * GOOGLE_CLIENT_SECRET=<google-oauth-client-secret>
 * ```
 * 
 * ## Configuration Details
 * 
 * ### NextAuth Options (app/api/auth/[...nextauth]/route.ts)
 * 
 * - **Providers**: GitHub and Google OAuth providers
 * - **Session Strategy**: JWT (stateless sessions)
 * - **Session Expiry**: 30 days
 * - **Callbacks**: 
 *   - jwt: Adds custom claims to token
 *   - session: Enriches session object
 *   - redirect: Controls post-login redirects
 *   - signIn: Custom sign-in logic
 * 
 * ### Route Protection (proxy.ts)
 * 
 * - Protected routes: /dashboard
 * - Public routes: /, /auth/signin, /api/auth, /auth/error
 * - Redirects unauthenticated users to /auth/signin
 * - Uses session cookies for detection
 * 
 * ## Usage Examples
 * 
 * ### Server Component (getting current user)
 * 
 * ```typescript
 * import { getCurrentSession } from '@/lib/auth';
 * 
 * export default async function ServerComponent() {
 *   const session = await getCurrentSession();
 *   
 *   if (!session?.user) {
 *     return <div>Not authenticated</div>;
 *   }
 *   
 *   return <div>Welcome, {session.user.name}</div>;
 * }
 * ```
 * 
 * ### Client Component (using useAuth hook)
 * 
 * ```typescript
 * 'use client';
 * 
 * import { useAuth } from '@/hooks/useAuth';
 * 
 * export default function ClientComponent() {
 *   const { user, isAuthenticated, isLoading } = useAuth();
 *   
 *   if (isLoading) return <div>Loading...</div>;
 *   
 *   return (
 *     <div>
 *       {isAuthenticated ? (
 *         <div>Hello, {user?.name}</div>
 *       ) : (
 *         <div>Please sign in</div>
 *       )}
 *     </div>
 *   );
 * }
 * ```
 * 
 * ### Protected Route Pattern
 * 
 * Use the useAuth hook with redirect:
 * 
 * ```typescript
 * 'use client';
 * 
 * import { useAuth } from '@/hooks/useAuth';
 * 
 * export default function ProtectedPage() {
 *   const { user, isLoading } = useAuth({
 *     redirectTo: '/auth/signin',
 *     redirectIfFound: false,
 *   });
 *   
 *   if (isLoading) return <div>Loading...</div>;
 *   
 *   return <div>Protected content for {user?.email}</div>;
 * }
 * ```
 * 
 * ### Sign In Flow
 * 
 * Users click "Continue with GitHub/Google" → NextAuth OAuth flow → 
 * Callback to /api/auth/callback/{provider} → Session created → 
 * Redirect to /dashboard
 * 
 * ## Security Considerations
 * 
 * 1. **NEXTAUTH_SECRET**: Must be a strong, random 64-character string
 *    - Generate with: `openssl rand -base64 32`
 * 
 * 2. **Session Tokens**: Stored in httpOnly cookies (secure)
 *    - Not accessible from JavaScript
 *    - Automatically sent with requests
 * 
 * 3. **JWT Validation**: 
 *    - Tokens are signed and verified
 *    - Tampered tokens are rejected
 * 
 * 4. **CSRF Protection**: 
 *    - NextAuth automatically handles CSRF tokens
 * 
 * 5. **Redirect Validation**:
 *    - Only allows same-origin redirects
 *    - Prevents open redirect attacks
 * 
 * 6. **OAuth Security**:
 *    - Uses authorization code flow (secure)
 *    - State parameter prevents CSRF
 * 
 * ## Error Handling
 * 
 * ### Common Errors
 * 
 * 1. **OAuthSignin**: OAuth provider misconfiguration
 *    - Check client ID and secret
 *    - Verify callback URLs
 * 
 * 2. **OAuthCallback**: Error processing OAuth response
 *    - Network issues
 *    - Provider returned error
 * 
 * 3. **SessionCallback**: Error in session callback
 *    - JWT token invalid
 *    - Session data corrupted
 * 
 * 4. **AccessDenied**: User not authorized
 *    - Custom signIn callback rejected
 * 
 * ### Error Page
 * 
 * Errors are displayed at `/auth/error?error=<ErrorCode>`
 * with user-friendly messages.
 * 
 * ## Testing
 * 
 * 1. **Local Development**:
 *    - NEXTAUTH_SECRET can be any string
 *    - NEXTAUTH_URL should be http://localhost:3000
 * 
 * 2. **OAuth Setup**:
 *    - GitHub: https://github.com/settings/developers
 *    - Google: https://console.cloud.google.com/apis/credentials
 * 
 * 3. **Testing Sign In**:
 *    - Click "Continue with GitHub/Google"
 *    - Authorize app
 *    - Should redirect to /dashboard
 * 
 * ## Deployment
 * 
 * ### Vercel
 * 
 * 1. Set environment variables in Vercel dashboard
 * 2. Update NEXTAUTH_URL to production URL
 * 3. Deploy
 * 
 * ### Self-Hosted
 * 
 * 1. Set NEXTAUTH_SECRET to strong random value
 * 2. Set NEXTAUTH_URL to production URL
 * 3. Ensure HTTPS for production
 * 4. Update OAuth callback URLs
 * 5. Deploy
 * 
 * ## Performance Optimizations
 * 
 * 1. **Session Refetch**: Set to 5 minutes (configurable)
 * 2. **Window Focus**: Auto-refresh on window focus
 * 3. **Reconnect**: Auto-refresh on network reconnect
 * 4. **JWT Strategy**: Stateless, no database queries
 * 
 * ## Troubleshooting
 * 
 * ### Session not persisting
 * 
 * - Check NEXTAUTH_SECRET is set
 * - Verify cookie settings in browser
 * - Check session strategy is JWT
 * 
 * ### Login redirect loop
 * 
 * - Check callback URL in OAuth provider settings
 * - Verify NEXTAUTH_URL matches deployment URL
 * - Check redirect callback logic
 * 
 * ### "Access Denied" error
 * 
 * - Check signIn callback returning true
 * - Verify user data from OAuth provider
 * - Check browser console for errors
 * 
 * ## Additional Resources
 * 
 * - NextAuth.js docs: https://next-auth.js.org
 * - GitHub OAuth: https://docs.github.com/en/developers/apps/building-oauth-apps
 * - Google OAuth: https://developers.google.com/identity/protocols/oauth2
 * - Next.js: https://nextjs.org/docs
 */

export const AUTHENTICATION_GUIDE = "See comments in this file for full documentation";
