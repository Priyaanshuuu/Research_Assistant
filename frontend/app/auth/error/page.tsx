"use client";

import { useSearchParams } from "next/navigation";
import Link from "next/link";

/**
 * Auth error page - displays authentication errors
 */
export default function AuthErrorPage() {
  const searchParams = useSearchParams();
  const error = searchParams.get("error");

  const getErrorMessage = (errorCode: string | null) => {
    const errorMessages: Record<string, { title: string; description: string }> = {
      Callback: {
        title: "Callback Error",
        description: "There was an error while processing your authentication callback.",
      },
      OAuthSignin: {
        title: "OAuth Sign In Error",
        description:
          "Error constructing an authorization URL. This usually means the provider is misconfigured.",
      },
      OAuthCallback: {
        title: "OAuth Callback Error",
        description:
          "Error handling the OAuth callback. Please try signing in again.",
      },
      OAuthCreateAccount: {
        title: "OAuth Account Creation Error",
        description:
          "Error creating a new account. Please try again or contact support.",
      },
      EmailCreateAccount: {
        title: "Email Account Creation Error",
        description:
          "Error creating an account with email. Please try again.",
      },
      EmailSignInError: {
        title: "Email Sign In Error",
        description: "Email sign in failed. Please try again.",
      },
      CredentialsSignin: {
        title: "Invalid Credentials",
        description: "The credentials provided were invalid.",
      },
      SessionCallback: {
        title: "Session Error",
        description: "Error in session callback. Please sign in again.",
      },
      AccessDenied: {
        title: "Access Denied",
        description:
          "You do not have permission to sign in. Please contact support.",
      },
      Verification: {
        title: "Verification Error",
        description: "Verification token not found or expired. Please sign in again.",
      },
    };

    return (
      errorMessages[errorCode || ""] || {
        title: "Authentication Error",
        description:
          "An unexpected error occurred during authentication. Please try again.",
      }
    );
  };

  const errorInfo = getErrorMessage(error);

  return (
    <div className="min-h-screen bg-linear-to-br from-red-50 to-red-100 flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-2xl shadow-lg p-8 space-y-6">
          {/* Error Icon */}
          <div className="flex justify-center">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
              <svg
                className="w-8 h-8 text-red-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4v.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
          </div>

          {/* Error Details */}
          <div className="text-center space-y-2">
            <h1 className="text-2xl font-bold text-gray-900">{errorInfo.title}</h1>
            <p className="text-gray-600">{errorInfo.description}</p>
          </div>

          {/* Error Code */}
          {error && (
            <div className="bg-gray-50 rounded-lg p-3 text-center">
              <p className="text-sm text-gray-500">
                Error Code: <span className="font-mono font-semibold">{error}</span>
              </p>
            </div>
          )}

          {/* Actions */}
          <div className="space-y-3 pt-4">
            <Link
              href="/auth/signin"
              className="block w-full text-center px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
            >
              Try Again
            </Link>
            <Link
              href="/"
              className="block w-full text-center px-4 py-2 bg-gray-100 text-gray-900 font-semibold rounded-lg hover:bg-gray-200 transition-colors"
            >
              Go Home
            </Link>
          </div>

          {/* Support */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
            <p className="text-sm text-blue-900">
              Still having issues?{" "}
              <a
                href="mailto:support@example.com"
                className="font-semibold text-blue-600 hover:text-blue-700"
              >
                Contact Support
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
