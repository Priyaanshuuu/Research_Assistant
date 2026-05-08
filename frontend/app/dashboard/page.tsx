"use client";

import { useSession, signOut } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { formatUserName, getInitials } from "@/lib/utils";

export default function DashboardPage() {
  const { data: session, status } = useSession();
  const router = useRouter();


  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/auth/signin");
    }
  }, [status, router]);

  if (status === "loading") {
    return (
      <div className="min-h-screen bg-linear-to-br from-slate-50 to-slate-100 flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="w-12 h-12 mx-auto animate-spin">
            <div className="w-full h-full border-4 border-gray-300 border-t-blue-600 rounded-full"></div>
          </div>
          <p className="text-gray-600 font-medium">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  if (status === "unauthenticated" || !session?.user) {
    return null;
  }

  const user = session.user;
  const displayName = formatUserName(user.name);
  const initials = getInitials(user.name);

  return (
    <div className="min-h-screen bg-linear-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Research Assistant</h1>
          <button
            onClick={() => signOut({ redirect: true, callbackUrl: "/" })}
            className="px-4 py-2 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700 transition-colors"
          >
            Sign Out
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex flex-col items-center justify-center min-h-[calc(100vh-200px)]">
          {/* Welcome Card */}
          <div className="bg-white rounded-2xl shadow-lg p-12 max-w-md w-full space-y-8">
            {/* User Avatar */}
            <div className="flex justify-center">
              {user.image ? (
                <img
                  src={user.image}
                  alt={user.name || "User"}
                  className="w-20 h-20 rounded-full border-4 border-blue-600 object-cover"
                />
              ) : (
                <div className="w-20 h-20 bg-linear-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center border-4 border-blue-600">
                  <span className="text-white text-2xl font-bold">{initials}</span>
                </div>
              )}
            </div>

            {/* Welcome Message */}
            <div className="text-center space-y-2">
              <h2 className="text-3xl font-bold text-gray-900">
                Welcome, {displayName}!
              </h2>
              <p className="text-gray-600">
                You are successfully authenticated to the Research Assistant
              </p>
            </div>

            {/* User Info */}
            <div className="space-y-4 pt-6 border-t border-gray-200">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <p className="text-gray-900 font-medium break-all">{user.email}</p>
              </div>

              {user.provider && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Authentication Provider
                  </label>
                  <div className="flex items-center gap-2">
                    <span className="text-gray-900 font-medium capitalize">
                      {user.provider}
                    </span>
                    {user.provider === "github" && (
                      <svg
                        className="w-4 h-4"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M10 0C4.477 0 0 4.484 0 10.017c0 4.425 2.865 8.18 6.839 9.49.5.092.682-.217.682-.482 0-.237-.008-.868-.013-1.703-2.782.603-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.463-1.11-1.463-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.544 2.914 1.19.092-.926.35-1.557.636-1.915-2.22-.253-4.555-1.112-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0110 4.766c.85.004 1.705.114 2.504.336 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C17.138 18.192 20 14.436 20 10.017 20 4.484 15.522 0 10 0z"
                          clipRule="evenodd"
                        />
                      </svg>
                    )}
                    {user.provider === "google" && (
                      <svg
                        className="w-4 h-4"
                        viewBox="0 0 24 24"
                        fill="currentColor"
                      >
                        <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                      </svg>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Features Preview */}
            <div className="bg-blue-50 rounded-lg p-4 space-y-2">
              <p className="text-sm font-semibold text-blue-900">Available Features:</p>
              <ul className="text-sm text-blue-800 space-y-1">
                <li className="flex items-center gap-2">
                  <span className="text-green-600">✓</span>
                  <span>Secure OAuth Authentication</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-600">✓</span>
                  <span>Protected Dashboard</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-green-600">✓</span>
                  <span>Session Management</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}




