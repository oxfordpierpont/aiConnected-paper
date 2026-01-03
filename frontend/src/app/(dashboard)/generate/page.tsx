"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { clientsApi, Client } from "@/lib/api/clients";
import { generationApi, GenerationJob } from "@/lib/api/generation";

const stepLabels: Record<string, string> = {
  topic_analysis: "Analyzing Topic",
  keyword_research: "Researching Keywords",
  web_research: "Web Research",
  outline_generation: "Creating Outline",
  content_writing: "Writing Content",
  statistics_extraction: "Extracting Statistics",
  pdf_rendering: "Rendering PDF",
};

function GeneratePageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const clientParam = searchParams.get("client");

  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [job, setJob] = useState<GenerationJob | null>(null);
  const [formData, setFormData] = useState({
    topic: "",
    client_id: clientParam || "",
    tone: "professional",
    custom_direction: "",
  });
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchClients = async () => {
      try {
        const response = await clientsApi.list();
        setClients(response.items);
        if (response.items.length > 0 && !formData.client_id) {
          setFormData((prev) => ({ ...prev, client_id: response.items[0].id }));
        }
      } catch (err) {
        console.error("Failed to fetch clients:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchClients();
  }, []);

  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (job && job.status !== "completed" && job.status !== "failed") {
      interval = setInterval(async () => {
        try {
          const updated = await generationApi.getJob(job.id);
          setJob(updated);

          if (updated.status === "completed") {
            router.push(`/documents`);
          }
        } catch (err) {
          console.error("Failed to fetch job status:", err);
        }
      }, 2000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [job, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setGenerating(true);

    try {
      const status = await generationApi.generate({
        topic: formData.topic,
        client_id: formData.client_id,
        tone: formData.tone,
        custom_direction: formData.custom_direction || undefined,
      });

      const jobData = await generationApi.getJob(status.job_id);
      setJob(jobData);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || "Failed to start generation");
      setGenerating(false);
    }
  };

  const handleCancel = async () => {
    if (!job) return;

    try {
      await generationApi.cancelJob(job.id);
      router.push("/documents");
    } catch (err) {
      console.error("Failed to cancel job:", err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <p className="text-gray-500">Loading...</p>
      </div>
    );
  }

  if (clients.length === 0) {
    return (
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">Generate Content</h1>
        <div className="bg-white rounded-lg shadow-sm border p-8 text-center">
          <p className="text-gray-500 mb-4">
            You need to add a client before generating content.
          </p>
          <button
            onClick={() => router.push("/clients")}
            className="px-4 py-2 bg-brand-primary text-white rounded-md hover:bg-brand-primary-light"
          >
            Add Your First Client
          </button>
        </div>
      </div>
    );
  }

  if (job) {
    return (
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">Generating Content</h1>
        <div className="bg-white rounded-lg shadow-sm border p-8">
          <div className="text-center mb-8">
            <div className="text-4xl font-bold text-brand-primary mb-2">
              {job.progress_percent}%
            </div>
            <div className="text-gray-600">
              {job.current_step
                ? stepLabels[job.current_step] || job.current_step
                : job.status === "completed"
                ? "Completed!"
                : job.status === "failed"
                ? "Failed"
                : "Starting..."}
            </div>
          </div>

          <div className="w-full bg-gray-200 rounded-full h-3 mb-6">
            <div
              className="bg-brand-primary h-3 rounded-full transition-all duration-500"
              style={{ width: `${job.progress_percent}%` }}
            />
          </div>

          <div className="space-y-2 mb-6">
            {Object.entries(stepLabels).map(([key, label]) => {
              const isActive = job.current_step === key;
              const isComplete =
                job.steps?.[key] !== undefined ||
                (job.progress_percent === 100 && job.status === "completed");

              return (
                <div
                  key={key}
                  className={`flex items-center gap-3 p-2 rounded ${
                    isActive ? "bg-blue-50" : ""
                  }`}
                >
                  <div
                    className={`w-5 h-5 rounded-full flex items-center justify-center text-xs ${
                      isComplete
                        ? "bg-green-500 text-white"
                        : isActive
                        ? "bg-blue-500 text-white animate-pulse"
                        : "bg-gray-200"
                    }`}
                  >
                    {isComplete ? "✓" : ""}
                  </div>
                  <span
                    className={
                      isActive
                        ? "font-medium"
                        : isComplete
                        ? "text-gray-500"
                        : "text-gray-400"
                    }
                  >
                    {label}
                  </span>
                </div>
              );
            })}
          </div>

          {job.status === "failed" && (
            <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-md mb-4">
              {job.error_message || "An error occurred during generation"}
            </div>
          )}

          <div className="flex justify-center gap-4">
            {job.status !== "completed" && job.status !== "failed" && (
              <button
                onClick={handleCancel}
                className="px-4 py-2 border rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
            )}
            {job.status === "completed" && (
              <button
                onClick={() => router.push("/documents")}
                className="px-4 py-2 bg-brand-primary text-white rounded-md hover:bg-brand-primary-light"
              >
                View Documents
              </button>
            )}
            {job.status === "failed" && (
              <>
                <button
                  onClick={() => {
                    setJob(null);
                    setGenerating(false);
                  }}
                  className="px-4 py-2 border rounded-md hover:bg-gray-50"
                >
                  Try Again
                </button>
                <button
                  onClick={() => router.push("/documents")}
                  className="px-4 py-2 text-gray-600 hover:underline"
                >
                  View Documents
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Generate Content</h1>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-md">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-sm border p-6 space-y-6">
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
            placeholder="Enter the topic for your content. E.g., 'The Future of AI in Healthcare: Transforming Patient Care Through Machine Learning'"
            required
          />
          <p className="text-xs text-gray-500 mt-1">
            Be specific about the topic. Better topics generate better content.
          </p>
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

        <div>
          <label className="block text-sm font-medium mb-1">
            Additional Direction (Optional)
          </label>
          <textarea
            value={formData.custom_direction}
            onChange={(e) =>
              setFormData((prev) => ({
                ...prev,
                custom_direction: e.target.value,
              }))
            }
            className="w-full px-3 py-2 border rounded-md"
            rows={2}
            placeholder="Any specific instructions or focus areas..."
          />
        </div>

        <div className="pt-4">
          <button
            type="submit"
            disabled={generating}
            className="w-full py-3 bg-brand-primary text-white rounded-md hover:bg-brand-primary-light disabled:opacity-50 text-lg font-medium"
          >
            {generating ? "Starting Generation..." : "Generate Content"}
          </button>
        </div>
      </form>
    </div>
  );
}

export default function GeneratePage() {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center min-h-[400px]">
          <p className="text-gray-500">Loading...</p>
        </div>
      }
    >
      <GeneratePageContent />
    </Suspense>
  );
}
