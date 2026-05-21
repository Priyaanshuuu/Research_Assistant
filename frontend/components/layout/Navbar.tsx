"use client";

import Link from "next/link";
import { useSession, signOut } from "next-auth/react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { FlaskConical, LogOut, PlusCircle } from "lucide-react";

export function Navbar() {
  const { data: session } = useSession();
  const router = useRouter();

  return (
    <nav className="border-b border-slate-200 bg-white sticky top-0 z-30">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
        {/* Logo */}
        <Link
          href="/dashboard"
          className="flex items-center gap-2 font-semibold text-slate-900 hover:text-slate-700"
        >
          <FlaskConical className="w-5 h-5 text-violet-600" />
          Research Assistant
        </Link>

        {/* Right side */}
        <div className="flex items-center gap-3">
          {session?.user && (
            <>
              <span className="text-sm text-slate-500 hidden sm:block">
                {session.user.email}
              </span>

              <Button
                variant="outline"
                size="sm"
                onClick={() => router.push("/research/new")}
                className="gap-1.5"
              >
                <PlusCircle className="w-4 h-4" />
                New Research
              </Button>

              <Button
                variant="ghost"
                size="sm"
                onClick={() => signOut({ callbackUrl: "/login" })}
                className="gap-1.5 text-slate-500"
              >
                <LogOut className="w-4 h-4" />
                <span className="hidden sm:block">Sign out</span>
              </Button>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}