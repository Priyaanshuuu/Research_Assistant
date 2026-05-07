"use client";

import { useEffect } from "react";
import Link from "next/link";

/**
 * Global error boundary component
 * Catches errors in all child components and displays error UI
 */
export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log error to error reporting service
    console.error("Global error:", error);
  }, [error]);

  return (
    <html lang="en">
      <body className="min-h-screen bg-gradient-to-br from-red-50 to-red-100 flex items-center justify-center px-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-lg p-8 space-y-6">
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
                  d="M12 9v2m0 4v2m0 0v2M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
          </div>

          {/* Error Details */}
          <div className="text-center space-y-2">
            <h2 className="text-2xl font-bold text-gray-900">Oops! Something went wrong</h2>
            <p className="text-gray-600">
              We encountered an unexpected error. Please try again.
            </p>
          </div>

          {/* Error Message */}
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-700 font-mono break-all">
              {error.message || "Unknown error occurred"}
            </p>
          </div>

          {/* Actions */}
          <div className="space-y-3 pt-4">
            <button
              onClick={reset}
              className="w-full px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
            >
              Try Again
            </button>
            <Link
              href="/"
              className="block w-full text-center px-4 py-2 bg-gray-100 text-gray-900 font-semibold rounded-lg hover:bg-gray-200 transition-colors"
            >
              Go Home
            </Link>
          </div>

          {/* Debug Info */}
          {error.digest && (
            <div className="text-center">
              <p className="text-xs text-gray-500">
                Error ID: <span className="font-mono">{error.digest}</span>
              </p>
            </div>
          )}
        </div>
      </body>
    </html>
  );
}
