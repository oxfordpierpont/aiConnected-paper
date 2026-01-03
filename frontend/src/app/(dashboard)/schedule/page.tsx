"use client";

import { useEffect, useState } from "react";
import { scheduleApi, ScheduledContent, ScheduleCreate } from "@/lib/api/schedule";
import { clientsApi, Client } from "@/lib/api/clients";

const statusColors: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-800",
  processing: "bg-blue-100 text-blue-800",
  completed: "bg-green-100 text-green-800",
  failed: "bg-red-100 text-red-800",
};

export default function SchedulePage() {
  const [schedules, setSchedules] = useState<ScheduledContent[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState<ScheduleCreate>({
    topic: "",
    scheduled_date: "",
    client_id: "",
  });
  const [saving, setSaving] = useState(false);

  const fetchData = async () => {
    try {
      const [scheduleRes, clientsRes] = await Promise.all([
        scheduleApi.list(),
        clientsApi.list(),
      ]);
      setSchedules(scheduleRes.items);
      setClients(clientsRes.items);
      if (clientsRes.items.length > 0 && !formData.client_id) {
        setFormData((prev) => ({ ...prev, client_id: clientsRes.items[0].id }));
      }
    } catch (error) {
      console.error("Failed to fetch data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);

    try {
      await scheduleApi.create(formData);
      setShowModal(false);
      setFormData({
        topic: "",
        scheduled_date: "",
        client_id: clients[0]?.id || "",
      });
      fetchData();
    } catch (error) {
      console.error("Failed to create schedule:", error);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this scheduled content?")) return;

    try {
      await scheduleApi.delete(id);
      fetchData();
    } catch (error) {
      console.error("Failed to delete schedule:", error);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  };

  const getClientName = (clientId: string) => {
    return clients.find((c) => c.id === clientId)?.name || "Unknown";
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Schedule</h1>
        <div className="flex gap-2">
          <button
            onClick={() => setShowModal(true)}
            className="px-4 py-2 bg-brand-primary text-white rounded-md hover:bg-brand-primary-light"
          >
            Schedule Content
          </button>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border">
        {loading ? (
          <div className="p-8 text-center text-gray-500">Loading...</div>
        ) : schedules.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <p>No scheduled content. Schedule content to automate your publishing.</p>
          </div>
        ) : (
          <div className="divide-y">
            {schedules.map((schedule) => (
              <div key={schedule.id} className="p-4 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <h3 className="font-medium">{schedule.topic}</h3>
                      <span
                        className={`px-2 py-0.5 text-xs font-medium rounded-full ${
                          statusColors[schedule.status]
                        }`}
                      >
                        {schedule.status}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 mt-1 text-sm text-gray-500">
                      <span>Client: {getClientName(schedule.client_id)}</span>
                      <span>Scheduled: {formatDate(schedule.scheduled_date)}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {schedule.status === "pending" && (
                      <button
                        onClick={() => handleDelete(schedule.id)}
                        className="px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 rounded-md"
                      >
                        Cancel
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-semibold mb-4">Schedule Content</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Client *</label>
                <select
                  value={formData.client_id}
                  onChange={(e) =>
                    setFormData((prev) => ({ ...prev, client_id: e.target.value }))
                  }
                  className="w-full px-3 py-2 border rounded-md"
                  required
                >
                  {clients.map((client) => (
                    <option key={client.id} value={client.id}>
                      {client.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Topic *</label>
                <textarea
                  value={formData.topic}
                  onChange={(e) =>
                    setFormData((prev) => ({ ...prev, topic: e.target.value }))
                  }
                  className="w-full px-3 py-2 border rounded-md"
                  rows={3}
                  placeholder="Enter the topic for scheduled content..."
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">
                  Scheduled Date *
                </label>
                <input
                  type="datetime-local"
                  value={formData.scheduled_date}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      scheduled_date: e.target.value,
                    }))
                  }
                  className="w-full px-3 py-2 border rounded-md"
                  required
                />
              </div>
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 border rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="px-4 py-2 bg-brand-primary text-white rounded-md hover:bg-brand-primary-light disabled:opacity-50"
                >
                  {saving ? "Scheduling..." : "Schedule"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
