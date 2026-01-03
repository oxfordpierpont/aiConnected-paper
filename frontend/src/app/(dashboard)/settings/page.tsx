"use client";

import { useEffect, useState } from "react";
import { agencyApi } from "@/lib/api/auth";
import { useAuthStore } from "@/stores/auth-store";

interface Agency {
  id: string;
  name: string;
  slug: string;
  website: string | null;
  primary_color: string;
  secondary_color: string;
}

export default function SettingsPage() {
  const { user } = useAuthStore();
  const [agency, setAgency] = useState<Agency | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    website: "",
    primary_color: "#1a4a6e",
    secondary_color: "#b8860b",
  });
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  useEffect(() => {
    const fetchAgency = async () => {
      try {
        const data = await agencyApi.getCurrent();
        setAgency(data);
        setFormData({
          name: data.name || "",
          website: data.website || "",
          primary_color: data.primary_color || "#1a4a6e",
          secondary_color: data.secondary_color || "#b8860b",
        });
      } catch (error) {
        console.error("Failed to fetch agency:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchAgency();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);

    try {
      await agencyApi.update(formData);
      setMessage({ type: "success", text: "Settings saved successfully" });
    } catch (error) {
      setMessage({ type: "error", text: "Failed to save settings" });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <p className="text-gray-500">Loading...</p>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Settings</h1>

      {message && (
        <div
          className={`mb-4 p-3 rounded-md ${
            message.type === "success"
              ? "bg-green-50 border border-green-200 text-green-700"
              : "bg-red-50 border border-red-200 text-red-700"
          }`}
        >
          {message.text}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="border-b pb-4 mb-4">
            <h2 className="text-lg font-semibold">General</h2>
            <p className="text-sm text-gray-500">Manage your agency settings</p>
          </div>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Agency Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, name: e.target.value }))
                }
                className="w-full max-w-md px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-brand-primary"
                placeholder="Your Agency"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Website</label>
              <input
                type="url"
                value={formData.website}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, website: e.target.value }))
                }
                className="w-full max-w-md px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-brand-primary"
                placeholder="https://example.com"
              />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="border-b pb-4 mb-4">
            <h2 className="text-lg font-semibold">Branding</h2>
            <p className="text-sm text-gray-500">Customize your brand colors</p>
          </div>
          <div className="grid grid-cols-2 gap-4 max-w-md">
            <div>
              <label className="block text-sm font-medium mb-1">
                Primary Color
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="color"
                  value={formData.primary_color}
                  onChange={(e) =>
                    setFormData((prev) => ({ ...prev, primary_color: e.target.value }))
                  }
                  className="w-10 h-10 border rounded cursor-pointer"
                />
                <input
                  type="text"
                  value={formData.primary_color}
                  onChange={(e) =>
                    setFormData((prev) => ({ ...prev, primary_color: e.target.value }))
                  }
                  className="flex-1 px-3 py-2 border rounded-md"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">
                Secondary Color
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="color"
                  value={formData.secondary_color}
                  onChange={(e) =>
                    setFormData((prev) => ({ ...prev, secondary_color: e.target.value }))
                  }
                  className="w-10 h-10 border rounded cursor-pointer"
                />
                <input
                  type="text"
                  value={formData.secondary_color}
                  onChange={(e) =>
                    setFormData((prev) => ({ ...prev, secondary_color: e.target.value }))
                  }
                  className="flex-1 px-3 py-2 border rounded-md"
                />
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="border-b pb-4 mb-4">
            <h2 className="text-lg font-semibold">Account</h2>
            <p className="text-sm text-gray-500">Your account information</p>
          </div>
          <div className="space-y-2 text-sm">
            <p>
              <span className="text-gray-500">Email:</span>{" "}
              <span className="font-medium">{user?.email}</span>
            </p>
            <p>
              <span className="text-gray-500">Role:</span>{" "}
              <span className="font-medium capitalize">{user?.role?.replace("_", " ")}</span>
            </p>
            <p>
              <span className="text-gray-500">Agency ID:</span>{" "}
              <span className="font-mono text-xs">{agency?.id}</span>
            </p>
          </div>
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="px-6 py-2 bg-brand-primary text-white rounded-md hover:bg-brand-primary-light disabled:opacity-50"
          >
            {saving ? "Saving..." : "Save Changes"}
          </button>
        </div>
      </form>
    </div>
  );
}
