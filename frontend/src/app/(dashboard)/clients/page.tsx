"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { clientsApi, Client, ClientCreate } from "@/lib/api/clients";

export default function ClientsPage() {
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingClient, setEditingClient] = useState<Client | null>(null);
  const [formData, setFormData] = useState<ClientCreate>({
    name: "",
    industry: "",
    website: "",
    location: "",
    description: "",
    tone: "professional",
  });
  const [saving, setSaving] = useState(false);

  const fetchClients = async () => {
    try {
      const response = await clientsApi.list();
      setClients(response.items);
    } catch (error) {
      console.error("Failed to fetch clients:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClients();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);

    try {
      if (editingClient) {
        await clientsApi.update(editingClient.id, formData);
      } else {
        await clientsApi.create(formData);
      }
      setShowModal(false);
      setEditingClient(null);
      setFormData({
        name: "",
        industry: "",
        website: "",
        location: "",
        description: "",
        tone: "professional",
      });
      fetchClients();
    } catch (error) {
      console.error("Failed to save client:", error);
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (client: Client) => {
    setEditingClient(client);
    setFormData({
      name: client.name,
      industry: client.industry || "",
      website: client.website || "",
      location: client.location || "",
      description: client.description || "",
      tone: client.tone,
    });
    setShowModal(true);
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this client?")) return;

    try {
      await clientsApi.delete(id);
      fetchClients();
    } catch (error) {
      console.error("Failed to delete client:", error);
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Clients</h1>
        <button
          onClick={() => {
            setEditingClient(null);
            setFormData({
              name: "",
              industry: "",
              website: "",
              location: "",
              description: "",
              tone: "professional",
            });
            setShowModal(true);
          }}
          className="px-4 py-2 bg-brand-primary text-white rounded-md hover:bg-brand-primary-light"
        >
          Add Client
        </button>
      </div>

      <div className="bg-white rounded-lg shadow-sm border">
        {loading ? (
          <div className="p-8 text-center text-gray-500">Loading...</div>
        ) : clients.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <p>No clients yet. Add your first client to get started.</p>
          </div>
        ) : (
          <div className="divide-y">
            {clients.map((client) => (
              <div
                key={client.id}
                className="p-4 flex items-center justify-between hover:bg-gray-50"
              >
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-brand-primary/10 rounded-full flex items-center justify-center text-brand-primary font-semibold">
                    {client.name.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <div className="font-medium">{client.name}</div>
                    <div className="text-sm text-gray-500">
                      {client.industry || "No industry"} • {client.location || "No location"}
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Link
                    href={`/generate?client=${client.id}`}
                    className="px-3 py-1.5 text-sm text-brand-primary hover:bg-brand-primary/10 rounded-md"
                  >
                    Generate
                  </Link>
                  <button
                    onClick={() => handleEdit(client)}
                    className="px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-md"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(client.id)}
                    className="px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 rounded-md"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-semibold mb-4">
              {editingClient ? "Edit Client" : "Add New Client"}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Name *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData((prev) => ({ ...prev, name: e.target.value }))
                  }
                  className="w-full px-3 py-2 border rounded-md"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Industry</label>
                <input
                  type="text"
                  value={formData.industry}
                  onChange={(e) =>
                    setFormData((prev) => ({ ...prev, industry: e.target.value }))
                  }
                  className="w-full px-3 py-2 border rounded-md"
                  placeholder="e.g., Technology, Healthcare"
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
                  className="w-full px-3 py-2 border rounded-md"
                  placeholder="https://example.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Location</label>
                <input
                  type="text"
                  value={formData.location}
                  onChange={(e) =>
                    setFormData((prev) => ({ ...prev, location: e.target.value }))
                  }
                  className="w-full px-3 py-2 border rounded-md"
                  placeholder="e.g., New York, NY"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      description: e.target.value,
                    }))
                  }
                  className="w-full px-3 py-2 border rounded-md"
                  rows={3}
                  placeholder="Brief description of the client..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Tone</label>
                <select
                  value={formData.tone}
                  onChange={(e) =>
                    setFormData((prev) => ({ ...prev, tone: e.target.value }))
                  }
                  className="w-full px-3 py-2 border rounded-md"
                >
                  <option value="professional">Professional</option>
                  <option value="casual">Casual</option>
                  <option value="authoritative">Authoritative</option>
                  <option value="friendly">Friendly</option>
                </select>
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
                  {saving ? "Saving..." : editingClient ? "Update" : "Create"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
