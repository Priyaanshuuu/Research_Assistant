import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Providers } from "./providers";
import { Toaster } from "sonner";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Research Assistant",
  description: "AI-powered multi-agent research assistant",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>{children}</Providers>
        <Toaster
          position="bottom-right"
          toastOptions={{
            classNames: {
              toast: "text-sm",
              error: "bg-red-50 border-red-200 text-red-800",
              success: "bg-green-50 border-green-200 text-green-800",
            },
          }}
        />
      </body>
    </html>
  );
}