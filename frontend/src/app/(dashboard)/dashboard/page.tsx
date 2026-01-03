"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { agencyApi, AgencyStats } from "@/lib/api/auth";
import { useAuthStore } from "@/stores/auth-store";

export default function DashboardPage() {
  const { user } = useAuthStore();
  const [stats, setStats] = useState<AgencyStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await agencyApi.getStats();
        setStats(data);
      } catch (error) {
        console.error("Failed to fetch stats:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-gray-600">
            Welcome back, {user?.first_name || "User"}!
          </p>
        </div>
        <Link
          href="/generate"
          className="px-4 py-2 bg-brand-primary text-white rounded-md hover:bg-brand-primary-light"
        >
          Generate Content
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Clients"
          value={loading ? "-" : stats?.total_clients ?? 0}
          href="/clients"
          color="blue"
        />
        <StatCard
          title="Documents"
          value={loading ? "-" : stats?.total_documents ?? 0}
          href="/documents"
          color="green"
        />
        <StatCard
          title="Scheduled"
          value={loading ? "-" : stats?.scheduled_content ?? 0}
          href="/schedule"
          color="orange"
        />
        <StatCard
          title="This Month"
          value={loading ? "-" : stats?.documents_this_month ?? 0}
          color="purple"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <Link
              href="/clients/new"
              className="block p-3 rounded-md border hover:bg-gray-50 transition-colors"
            >
              <div className="font-medium">Add New Client</div>
              <div className="text-sm text-gray-500">
                Create a new client profile to generate content for
              </div>
            </Link>
            <Link
              href="/generate"
              className="block p-3 rounded-md border hover:bg-gray-50 transition-colors"
            >
              <div className="font-medium">Generate Content</div>
              <div className="text-sm text-gray-500">
                Create professional thought leadership content
              </div>
            </Link>
            <Link
              href="/schedule"
              className="block p-3 rounded-md border hover:bg-gray-50 transition-colors"
            >
              <div className="font-medium">Schedule Content</div>
              <div className="text-sm text-gray-500">
                Plan and schedule future content generation
              </div>
            </Link>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h2 className="text-lg font-semibold mb-4">Recent Documents</h2>
          <div className="text-gray-500 text-sm">
            {loading ? (
              <p>Loading...</p>
            ) : stats?.total_documents === 0 ? (
              <div className="text-center py-6">
                <p className="mb-4">No documents yet</p>
                <Link
                  href="/generate"
                  className="text-brand-primary hover:underline"
                >
                  Generate your first document
                </Link>
              </div>
            ) : (
              <Link
                href="/documents"
                className="text-brand-primary hover:underline"
              >
                View all documents →
              </Link>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

interface StatCardProps {
  title: string;
  value: number | string;
  href?: string;
  color: "blue" | "green" | "orange" | "purple";
}

function StatCard({ title, value, href, color }: StatCardProps) {
  const colorClasses = {
    blue: "border-l-blue-500",
    green: "border-l-green-500",
    orange: "border-l-orange-500",
    purple: "border-l-purple-500",
  };

  const content = (
    <div
      className={`bg-white p-6 rounded-lg shadow-sm border border-l-4 ${colorClasses[color]} ${
        href ? "hover:shadow-md transition-shadow cursor-pointer" : ""
      }`}
    >
      <div className="text-sm text-gray-500">{title}</div>
      <div className="text-3xl font-bold mt-2">{value}</div>
    </div>
  );

  if (href) {
    return <Link href={href}>{content}</Link>;
  }

  return content;
}
