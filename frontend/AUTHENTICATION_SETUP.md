# Production-Grade Next.js Authentication Setup

## Overview

This is a complete, production-grade authentication system built with Next.js 16, NextAuth.js, and OAuth 2.0 (GitHub & Google). It implements modern best practices for security, performance, and user experience.

## Features

✅ **OAuth 2.0 Authentication**
- GitHub provider
- Google provider
- Extensible for additional providers

✅ **Security**
- JWT-based stateless sessions
- Secure httpOnly cookies
- CSRF protection (built-in)
- Signed and verified tokens
- Open redirect prevention
- Secure password practices (OAuth eliminates this)

✅ **Session Management**
- 30-day session duration
- Auto-refresh on window focus
- Auto-refresh on network reconnect
- 5-minute session check interval
- Configurable session parameters

✅ **Route Protection**
- Server-side proxy.ts protection
- Client-side useAuth hook
- Automatic redirects to signin
- Callback URL support

✅ **User Experience**
- Beautiful, modern UI with Tailwind CSS
- Loading states
- Error handling with user-friendly messages
- Responsive design
- Smooth animations

✅ **Developer Experience**
- TypeScript support
- Comprehensive type definitions
- Custom hooks for auth
- Utility functions
- Validation helpers
- Logging utilities
- Environment variable validation

## Architecture

### File Structure

```
frontend/
├── app/
│   ├── api/auth/[...nextauth]/
│   │   └── route.ts              # NextAuth core configuration
│   ├── auth/
│   │   ├── signin/page.tsx       # Sign-in page with OAuth buttons
│   │   └── error/page.tsx        # Error display page
│   ├── dashboard/
│   │   └── page.tsx              # Protected dashboard (shows user info)
│   ├── layout.tsx                # Root layout with SessionProvider
│   ├── page.tsx                  # Landing page
│   ├── error.tsx                 # Error boundary
│   ├── global-error.tsx          # Global error handler
│   ├── not-found.tsx             # 404 page
│   └── providers.tsx             # SessionProvider wrapper
├── lib/
│   ├── auth.ts                   # Server-side auth helpers
│   ├── constants.ts              # Auth routes and constants
│   ├── env.ts                    # Environment validation
│   ├── logger.ts                 # Logging utilities
│   ├── storage.ts                # LocalStorage utilities
│   ├── utils.ts                  # General utilities
│   └── validation.ts             # Input validation
├── hooks/
│   └── useAuth.ts                # Custom useAuth hook
├── types/
│   └── auth.ts                   # TypeScript types
├── proxy.ts                      # Route protection middleware
├── next.config.ts                # Next.js configuration
├── tsconfig.json                 # TypeScript config
├── package.json                  # Dependencies
└── .env.local                    # Environment variables
```

## Setup Instructions

### 1. Clone Repository

```bash
cd frontend
npm install
```

### 2. Create OAuth Applications

#### GitHub OAuth App
1. Go to https://github.com/settings/developers
2. Click "New OAuth App"
3. Fill in details:
   - Application name: Research Assistant
   - Homepage URL: http://localhost:3000 (for dev)
   - Authorization callback URL: http://localhost:3000/api/auth/callback/github
4. Copy Client ID and Client Secret

#### Google OAuth App
1. Go to https://console.cloud.google.com/apis/credentials
2. Click "Create Credentials" → "OAuth Client ID"
3. Select Application type: Web application
4. Add Authorized JavaScript origins:
   - http://localhost:3000
5. Add Authorized redirect URIs:
   - http://localhost:3000/api/auth/callback/google
6. Copy Client ID and Client Secret

### 3. Environment Variables

Create `.env.local`:

```bash
# NextAuth
NEXTAUTH_SECRET=<64-char-random-string>
NEXTAUTH_URL=http://localhost:3000

# GitHub OAuth
GITHUB_ID=<your-github-client-id>
GITHUB_SECRET=<your-github-client-secret>

# Google OAuth
GOOGLE_CLIENT_ID=<your-google-client-id>
GOOGLE_CLIENT_SECRET=<your-google-client-secret>
```

**Generate NEXTAUTH_SECRET:**
```bash
openssl rand -base64 32
# Output: <64-char-string>
```

### 4. Run Development Server

```bash
npm run dev
```

Visit http://localhost:3000

### 5. Test Authentication

1. Click "Get Started" on landing page
2. Choose GitHub or Google
3. Authorize application
4. Should redirect to dashboard showing your name
5. Click "Sign Out" to log out

## Usage Guide

### Server Components (Getting Current User)

```typescript
// app/dashboard/page.tsx
import { getAuthenticatedUser } from '@/lib/auth';

export default async function Dashboard() {
  const user = await getAuthenticatedUser();
  
  if (!user) {
    redirect('/auth/signin');
  }
  
  return <div>Welcome, {user.name}</div>;
}
```

### Client Components (Using useAuth Hook)

```typescript
'use client';

import { useAuth } from '@/hooks/useAuth';

export default function Profile() {
  const { user, isLoading } = useAuth();
  
  if (isLoading) return <div>Loading...</div>;
  
  return <div>Hello, {user?.name}</div>;
}
```

### Protected Routes

```typescript
'use client';

import { useAuth } from '@/hooks/useAuth';

export default function ProtectedPage() {
  const { isAuthenticated, isLoading } = useAuth({
    redirectTo: '/auth/signin',
  });
  
  if (isLoading) return null;
  
  return <div>This page is protected</div>;
}
```

### Signing Out

```typescript
import { signOut } from 'next-auth/react';

export default function SignOutButton() {
  return (
    <button onClick={() => signOut({ redirect: true, callbackUrl: '/' })}>
      Sign Out
    </button>
  );
}
```

## Security Best Practices

### 1. Environment Variables

- **NEXTAUTH_SECRET**: Must be strong and random (64 characters minimum)
- Never commit `.env.local` to version control
- Use different secrets for different environments
- Rotate secrets periodically in production

### 2. OAuth Configuration

- Always use HTTPS in production
- Verify callback URLs match exactly
- Keep client secrets secret (server-side only)
- Monitor OAuth app activity

### 3. Session Management

- JWT tokens are signed and verified
- Sessions expire after 30 days
- Tokens cannot be tampered with
- Use secure cookies (httpOnly, secure in prod)

### 4. Route Protection

- `proxy.ts` prevents unauthorized access
- Unauthenticated users redirected to signin
- Works at the request level (very secure)
- Works even with client-side JS disabled

### 5. CSRF Protection

- NextAuth handles CSRF tokens automatically
- No additional configuration needed
- Verified on every state-changing operation

## Deployment Guide

### Vercel (Recommended)

1. Push code to GitHub/GitLab
2. Import in Vercel dashboard
3. Set environment variables:
   ```
   NEXTAUTH_SECRET=<strong-random-string>
   NEXTAUTH_URL=https://yourdomain.com
   GITHUB_ID=<github-id>
   GITHUB_SECRET=<github-secret>
   GOOGLE_CLIENT_ID=<google-id>
   GOOGLE_CLIENT_SECRET=<google-secret>
   ```
4. Deploy

### Self-Hosted (Linux/Docker)

1. Generate strong NEXTAUTH_SECRET:
   ```bash
   openssl rand -base64 32
   ```

2. Update environment variables to production URLs
3. Update OAuth callback URLs in GitHub/Google
4. Build and deploy:
   ```bash
   npm run build
   npm start
   ```

## Troubleshooting

### "Session not persisting"
- Verify NEXTAUTH_SECRET is set
- Check cookies are enabled in browser
- Ensure NEXTAUTH_URL matches your domain
- Check browser DevTools → Application → Cookies

### "Login redirect loop"
- Verify callback URL in OAuth provider settings
- Check NEXTAUTH_URL matches your deployment
- Look at browser console for errors
- Check proxy.ts matcher pattern

### "Access Denied" error
- Check OAuth credentials are correct
- Verify user email is available from OAuth provider
- Check signIn callback logic
- Review browser console errors

### "Missing environment variables"
- Run `npm run dev` to see missing variables
- Add all required env vars to .env.local
- Restart development server

## Performance Optimizations

### Session Refresh
- Configured to refresh every 5 minutes
- Auto-refreshes on window focus
- Auto-refreshes on network reconnect
- Prevents stale sessions

### Static Optimization
- Landing page pre-rendered
- Reduces Time to First Byte (TTFB)
- Improves SEO

### Image Optimization
- User avatars optimized via Next.js Image component
- Reduces page load time

## Monitoring & Analytics

### Session Events
All sign-in/sign-out events are logged:
```typescript
// Check console for events
console.log(`User signed in via ${provider}`);
```

### Error Tracking
Errors are logged to console and can be sent to error tracking service:
```typescript
// Implement in callbacks
catch (error) {
  console.error("Error:", error);
  // sendToErrorTracking(error);
}
```

## Common Customizations

### Add More OAuth Providers

1. Install provider: `npm install next-auth/providers/[provider]`
2. Import in route.ts:
   ```typescript
   import Provider from "next-auth/providers/[provider]";
   ```
3. Add to providers array in authOptions
4. Add callback URL to OAuth provider settings
5. Add client ID and secret to .env.local

### Change Session Duration

In `app/api/auth/[...nextauth]/route.ts`:
```typescript
session: {
  maxAge: 7 * 24 * 60 * 60, // 7 days instead of 30
}
```

### Custom User Data

In JWT callback:
```typescript
async jwt({ token, profile }) {
  if (profile) {
    token.customField = profile.customField;
  }
  return token;
}
```

### Database Integration

For storing user data in database:
1. Query database in signIn callback
2. Create user if doesn't exist
3. Return true to allow sign-in
4. Store/update user data

## Testing

### Manual Testing
1. Test GitHub login
2. Test Google login
3. Test logout
4. Test protected routes
5. Test error scenarios
6. Test session persistence

### Automated Testing
Can be added with Jest/Vitest:
```bash
npm install --save-dev jest @testing-library/react
```

## Production Checklist

- [ ] Environment variables configured
- [ ] OAuth apps created and URLs updated
- [ ] HTTPS enabled
- [ ] NEXTAUTH_SECRET is strong and random
- [ ] Proxy.ts route protection verified
- [ ] Error pages tested
- [ ] Security headers configured
- [ ] Session duration appropriate
- [ ] Email configuration (if needed)
- [ ] Monitoring/logging setup
- [ ] Backup and recovery plan
- [ ] Rate limiting (add if needed)

## Support & Documentation

- [NextAuth.js Docs](https://next-auth.js.org)
- [Next.js Docs](https://nextjs.org/docs)
- [OAuth 2.0 Security Best Practices](https://tools.ietf.org/html/rfc6749)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

## License

MIT

---

**Last Updated:** May 7, 2026
**Version:** 1.0.0
