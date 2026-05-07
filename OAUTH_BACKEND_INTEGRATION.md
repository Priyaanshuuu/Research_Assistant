# OAuth Backend Integration - Complete Setup Guide

## Overview

This document covers the production-grade OAuth user persistence implementation. When a user logs in via GitHub or Google, their profile is automatically saved to the Neon PostgreSQL database.

## Architecture

### Flow Diagram

```
1. User clicks "Continue with GitHub/Google"
        ↓
2. Frontend redirects to NextAuth OAuth handler
        ↓
3. OAuth provider authenticates user
        ↓
4. NextAuth creates session (JWT in httpOnly cookie)
        ↓
5. signIn callback triggered in route.ts
        ↓
6. Calls saveOAuthUserToDatabase from lib/auth.ts
        ↓
7. POST to backend /api/auth/oauth/upsert endpoint
        ↓
8. Backend validates and upserts user in Neon database
        ↓
9. Returns user data + JWT token (for future backend calls)
        ↓
10. Frontend redirects to /dashboard
        ↓
11. Dashboard displays user name (from session)
```

## Database Schema Changes

### Migration: 002_oauth_fields

Added three fields to `users` table:

```sql
-- Email verification flag (OAuth emails are pre-verified)
ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT false NOT NULL;

-- OAuth provider profile picture URL
ALTER TABLE users ADD COLUMN image TEXT;

-- Unique index on provider_id (with NULL handling for email-based users)
CREATE UNIQUE INDEX ix_users_provider_id_unique ON users (provider_id) 
WHERE provider_id IS NOT NULL;
```

### User Model Updated

```python
class User(Base):
    # ... existing fields ...
    email_verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    image: Mapped[str | None] = mapped_column(Text, nullable=True)
    provider: Mapped[AuthProvider]  # EMAIL, GOOGLE, or GITHUB
    provider_id: Mapped[str | None] = mapped_column(unique=True, index=True)
```

## Setup Instructions

### Step 1: Apply Database Migration

The migration file has been created at:
```
backend/db/migrations/versions/002_oauth_fields.py
```

Apply it to your Neon database:

```bash
cd backend
alembic upgrade head
```

This will add the three new columns to the users table.

**Verify in Neon Console**:
- Go to https://console.neon.tech/app/projects
- View your `neondb` database
- Check `users` table has columns: `email_verified`, `image`

### Step 2: Verify Environment Configuration

#### Frontend (`frontend/.env.local`)

```env
# NextAuth Configuration
NEXTAUTH_SECRET=29Zy6vS1zmMG59f9DJ+PtUeWU64nvg/a9WMcWSU8JkE=
NEXTAUTH_URL=http://localhost:3000

# OAuth Providers (from GitHub/Google developer settings)
GITHUB_ID=your_github_id
GITHUB_SECRET=your_github_secret
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_secret

# Backend API URL (for OAuth user persistence)
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

#### Backend (`backend/.env`)

```env
# Database
DATABASE_URL=postgresql://user:pass@host/database

# JWT for backend API tokens
JWT_SECRET_KEY=your-secure-secret-key-here

# CORS - allow frontend
CORS_ORIGINS=["http://localhost:3000"]

# Other services (optional for now)
OPENAI_API_KEY=optional
TAVILY_API_KEY=optional
PINECONE_API_KEY=optional
```

### Step 3: Start Services

#### Terminal 1 - Backend API

```bash
cd backend
python -m uvicorn main:app --reload
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

#### Terminal 2 - Frontend

```bash
cd frontend
npm run dev
```

Expected output:
```
▲ Next.js 16.2.4
- Local:        http://localhost:3000
```

### Step 4: Test OAuth Login

1. **Visit Landing Page**
   - Go to http://localhost:3000
   - Should see feature showcase and "Continue with GitHub" & "Continue with Google" buttons

2. **GitHub OAuth**
   - Click "Continue with GitHub"
   - Authorize the app (if first time)
   - Should redirect to /dashboard

3. **Verify Database Persistence**
   ```bash
   # In Neon console or psql:
   SELECT id, email, name, image, provider, email_verified FROM users;
   ```
   
   Expected result:
   ```
   id                 | email               | name      | image                           | provider | email_verified
   ------------------ | ------------------- | --------- | ------------------------------- | -------- | ------
   abc123..           | user@github.com     | GitHub User | https://avatars.github...      | github   | true
   ```

4. **Test Dashboard**
   - Dashboard should display:
     - User's name in center
     - User's email
     - User's avatar/initials
     - Sign out button

## Backend Implementation Details

### OAuth Upsert Endpoint

**Endpoint**: `POST /api/auth/oauth/upsert`

**Request**:
```json
{
  "email": "user@github.com",
  "name": "John Doe",
  "provider": "github",
  "provider_id": "12345",
  "image": "https://avatars.githubusercontent.com/u/12345"
}
```

**Validation**:
- Provider must be "github" or "google" (case-insensitive)
- Email must be valid format
- provider_id must not be empty
- Returns 400 Bad Request if validation fails

**Behavior**:
- **First login**: Creates new user with email_verified=true
- **Subsequent login**: Updates user's name, image, provider_id if changed
- **Response**: Returns JWT token for backend API access + user data

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "abc123...",
  "email": "user@github.com",
  "name": "John Doe",
  "image": "https://avatars.githubusercontent.com/u/12345",
  "provider": "github"
}
```

### Error Handling

The endpoint handles all error cases with appropriate HTTP status codes:

| Status | Scenario | Example |
|--------|----------|---------|
| 400 | Invalid provider | `"provider": "twitter"` |
| 400 | Missing email | Empty email field |
| 400 | Invalid email | `"email": "not-an-email"` |
| 400 | Missing provider_id | Empty provider_id field |
| 500 | Database error | Connection timeout, constraint violation |

All errors include descriptive messages in response.

### Logging

The endpoint logs all operations:

```
INFO:     OAuth user exists: user@github.com via github
INFO:     Updated provider for user@github.com: github
INFO:     Creating new OAuth user: newuser@github.com via github
INFO:     OAuth upsert successful: user@github.com (ID: abc123...)
WARN:     Invalid OAuth provider: unsupported
ERROR:    OAuth upsert error: ValueError - Invalid enum value
```

## Frontend Implementation Details

### saveOAuthUserToDatabase Function

**Location**: `lib/auth.ts`

**Called From**: NextAuth signIn callback in `app/api/auth/[...nextauth]/route.ts`

**Behavior**:
1. Validates user has email and provider
2. POST to backend `/api/auth/oauth/upsert`
3. Includes error handling
4. Graceful degradation: if backend is down, OAuth login still succeeds

**Graceful Degradation**:
- If backend unreachable: User still logged in via NextAuth
- Console shows warning: "User not persisted to database, but OAuth login allowed"
- User can still access dashboard
- Session works from NextAuth JWT, not backend

This ensures frontend remains operational even if backend has issues.

### signIn Callback Flow

```typescript
async signIn({ user, account }) {
  // 1. Check email exists
  if (!user?.email) return false;
  
  // 2. For OAuth only
  if (account?.provider) {
    // 3. Extract OAuth data
    const oauthData = {
      id: account.providerAccountId,        // OAuth provider's user ID
      name: user?.name,                      // From OAuth profile
      email: user?.email,                    // From OAuth profile
      image: user?.image,                    // From OAuth profile
      provider: account.provider,            // "github" or "google"
    };
    
    // 4. Call backend endpoint
    const result = await saveOAuthUserToDatabase(oauthData);
    
    // 5. If fails, log warning but allow login
    if (!result) {
      console.warn("User not persisted to database");
    }
  }
  
  return true;  // Always allow OAuth login
}
```

## Production Checklist

- [ ] Database migration applied to Neon
- [ ] All environment variables configured (see Step 2)
- [ ] Backend running and accessible from frontend
- [ ] CORS configured correctly (http://localhost:3000 for dev)
- [ ] Frontend OAuth buttons work and redirect to signin
- [ ] Database persistence verified after OAuth login
- [ ] Dashboard displays user info correctly
- [ ] Error handling tested (bad provider, missing fields, etc.)
- [ ] Logs show OAuth upsert operations

## Troubleshooting

### OAuth button doesn't work
**Symptom**: Click "Continue with GitHub/Google" → No redirect
**Causes**:
- OAuth credentials invalid (check GITHUB_ID, GOOGLE_CLIENT_ID)
- Callback URLs not configured in OAuth app settings
- NEXTAUTH_SECRET missing or invalid

**Fix**:
1. Verify OAuth app callback URLs are set:
   - GitHub: http://localhost:3000/api/auth/callback/github
   - Google: http://localhost:3000/api/auth/callback/google
2. Check frontend console for errors
3. Regenerate NEXTAUTH_SECRET: `openssl rand -base64 32`

### OAuth login succeeds but user not in database
**Symptom**: Dashboard loads, but Neon database has no user
**Cause**: Frontend → Backend communication failed

**Debug**:
1. Check browser console for errors during login
2. Check backend logs for POST to `/api/auth/oauth/upsert`
3. Verify NEXT_PUBLIC_API_URL is correct
4. Verify backend CORS allows http://localhost:3000

**Fix**:
```bash
# Check backend logs
tail -f backend.log

# Verify endpoint manually
curl -X POST http://127.0.0.1:8000/api/auth/oauth/upsert \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "provider": "github",
    "provider_id": "123456",
    "image": "https://example.com/avatar.jpg"
  }'
```

### Dashboard doesn't show user name
**Symptom**: Dashboard loads but user info is blank
**Cause**: Session not created properly

**Fix**:
1. Check browser DevTools → Application → Cookies
2. Should have `next-auth.jwt` and `next-auth.session-token`
3. If missing, OAuth login failed - check signIn callback errors

### Migration fails
**Symptom**: `alembic upgrade head` error
**Cause**: Migration already applied or database connection error

**Debug**:
```bash
# Check migration status
alembic current
alembic history

# Check Neon connection
psql $DATABASE_URL -c "\d users"
```

## Next Steps

1. **Test full flow**: Complete the test steps in Step 4
2. **Monitor logs**: Check both frontend and backend logs during login
3. **Verify database**: Query Neon to confirm users are persisting
4. **Dashboard**: Ensure user info displays correctly on dashboard

## Related Files

- [AUTHENTICATION_SETUP.md](./AUTHENTICATION_SETUP.md) - Frontend OAuth setup
- [backend/api/routes/auth.py](./backend/api/routes/auth.py) - Backend OAuth endpoint
- [backend/db/models.py](./backend/db/models.py) - User model with OAuth fields
- [frontend/lib/auth.ts](./frontend/lib/auth.ts) - Frontend auth utilities
- [frontend/app/api/auth/\[...nextauth\]/route.ts](./frontend/app/api/auth/[...nextauth]/route.ts) - NextAuth configuration

## Questions?

Refer to:
- NextAuth docs: https://next-auth.js.org/
- Neon docs: https://neon.tech/docs/
- FastAPI CORS: https://fastapi.tiangolo.com/tutorial/cors/
