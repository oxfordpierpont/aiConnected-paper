"use client";

import { Bell, Search, User } from "lucide-react";

export function Header() {
  return (
    <header className="h-16 bg-white border-b flex items-center justify-between px-6">
      {/* Search */}
      <div className="flex items-center gap-2 bg-gray-100 rounded-md px-3 py-2 w-96">
        <Search className="h-4 w-4 text-gray-400" />
        <input
          type="text"
          placeholder="Search..."
          className="bg-transparent border-none outline-none text-sm flex-1"
        />
      </div>

      {/* Right section */}
      <div className="flex items-center gap-4">
        {/* Notifications */}
        <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md">
          <Bell className="h-5 w-5" />
        </button>

        {/* User menu */}
        <button className="flex items-center gap-2 p-2 hover:bg-gray-100 rounded-md">
          <div className="h-8 w-8 bg-brand-primary rounded-full flex items-center justify-center">
            <User className="h-4 w-4 text-white" />
          </div>
        </button>
      </div>
    </header>
  );
}
