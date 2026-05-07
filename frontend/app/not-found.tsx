import Link from "next/link";

/**
 * 404 Not Found page
 * Displayed when a route is not found
 */
export default function NotFound() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center px-4 py-12">
      <div className="max-w-md w-full text-center space-y-8">
        {/* 404 Text */}
        <div className="space-y-2">
          <h1 className="text-9xl font-bold text-gray-900">404</h1>
          <h2 className="text-3xl font-bold text-gray-900">Page Not Found</h2>
        </div>

        {/* Description */}
        <p className="text-gray-600 text-lg">
          Sorry, the page you're looking for doesn't exist or has been moved.
        </p>

        {/* SVG Illustration */}
        <div className="flex justify-center py-8">
          <svg
            className="w-48 h-48 text-gray-300"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1}
              d="M9 12l2 2m0 0l4-4m0 0l2-2m-2 2L7 7"
            />
          </svg>
        </div>

        {/* Action Buttons */}
        <div className="space-y-3 pt-4">
          <Link
            href="/"
            className="block px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
          >
            Go Home
          </Link>
          <Link
            href="/dashboard"
            className="block px-6 py-3 bg-gray-100 text-gray-900 font-semibold rounded-lg hover:bg-gray-200 transition-colors"
          >
            Go to Dashboard
          </Link>
        </div>

        {/* Help Text */}
        <p className="text-sm text-gray-500">
          If you think this is a mistake, please{" "}
          <a
            href="mailto:support@example.com"
            className="text-blue-600 hover:text-blue-700 font-semibold"
          >
            contact support
          </a>
        </p>
      </div>
    </div>
  );
}
