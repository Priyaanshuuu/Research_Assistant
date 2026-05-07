/**
 * Type definitions for authentication
 */

import type { DefaultSession, DefaultUser } from "next-auth";

declare module "next-auth" {
  interface Session extends DefaultSession {
    user: DefaultSession["user"] & {
      id?: string;
      provider?: string;
    };
  }

  interface User extends DefaultUser {
    provider?: string;
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    provider?: string;
    accessToken?: string;
  }
}

/**
 * User object with extended properties
 */
export interface AuthUser {
  id?: string;
  name?: string | null;
  email?: string | null;
  image?: string | null;
  provider?: string;
}

/**
 * Session object with extended properties
 */
export interface ExtendedSession {
  user?: AuthUser;
  expires: string;
}

/**
 * Auth error types
 */
export enum AuthErrorType {
  INVALID_CREDENTIALS = "INVALID_CREDENTIALS",
  SESSION_EXPIRED = "SESSION_EXPIRED",
  UNAUTHORIZED = "UNAUTHORIZED",
  OAUTH_ERROR = "OAUTH_ERROR",
  INTERNAL_ERROR = "INTERNAL_ERROR",
}

/**
 * Auth response
 */
export interface AuthResponse {
  success: boolean;
  error?: string;
  errorType?: AuthErrorType;
}
