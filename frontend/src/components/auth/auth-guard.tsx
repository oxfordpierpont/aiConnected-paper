"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth-store";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const [isHydrated, setIsHydrated] = useState(false);

  // Wait for Zustand to hydrate from localStorage
  useEffect(() => {
    setIsHydrated(true);
  }, []);

  // Check authentication after hydration
  useEffect(() => {
    if (!isHydrated) return; // Don't check until hydrated

    const token = localStorage.getItem("access_token");

    // If no token and no user, redirect to login
    if (!token && !user && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isHydrated, user, isAuthenticated, router]);

  // Show loading state while hydrating
  if (!isHydrated) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-gray-600">Loading...</div>
      </div>
    );
  }

  // Show loading if not authenticated yet (tokens exist but user not loaded)
  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
  if (token && !user) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-gray-600">Loading...</div>
      </div>
    );
  }

  return <>{children}</>;
}
