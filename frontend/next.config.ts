import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* Security and Performance Config */
  reactStrictMode: true,
  
  // Enable response compression
  compress: true,

  // Security headers
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          // Prevent clickjacking
          {
            key: "X-Frame-Options",
            value: "DENY",
          },
          // Prevent MIME type sniffing
          {
            key: "X-Content-Type-Options",
            value: "nosniff",
          },
          // Enable XSS protection
          {
            key: "X-XSS-Protection",
            value: "1; mode=block",
          },
          // Referrer policy
          {
            key: "Referrer-Policy",
            value: "strict-origin-when-cross-origin",
          },
          // Permissions policy
          {
            key: "Permissions-Policy",
            value: "accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()",
          },
        ],
      },
      {
        source: "/api/auth/:path*",
        headers: [
          {
            key: "Cache-Control",
            value: "no-store, no-cache, must-revalidate, proxy-revalidate",
          },
        ],
      },
    ];
  },

  // Redirect configuration for auth flows
  async redirects() {
    return [
      // Redirect /signin to /auth/signin
      {
        source: "/signin",
        destination: "/auth/signin",
        permanent: true,
      },
      // Redirect /login to /auth/signin
      {
        source: "/login",
        destination: "/auth/signin",
        permanent: true,
      },
    ];
  },

  // Environment variable validation is handled in lib/env.ts
  // which is imported and checked at build time
};

export default nextConfig;
