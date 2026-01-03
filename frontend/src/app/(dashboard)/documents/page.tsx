"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { documentsApi, Document } from "@/lib/api/documents";

const statusColors: Record<string, string> = {
  draft: "bg-gray-100 text-gray-800",
  generating: "bg-blue-100 text-blue-800",
  ready: "bg-green-100 text-green-800",
  distributed: "bg-purple-100 text-purple-800",
  failed: "bg-red-100 text-red-800",
};

const statusLabels: Record<string, string> = {
  draft: "Draft",
  generating: "Generating",
  ready: "Ready",
  distributed: "Distributed",
  failed: "Failed",
};

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>("");

  const fetchDocuments = async () => {
    try {
      const response = await documentsApi.list(1, 50, undefined, filter || undefined);
      setDocuments(response.items);
    } catch (error) {
      console.error("Failed to fetch documents:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [filter]);

  const handleDownload = async (doc: Document) => {
    try {
      const blob = await documentsApi.download(doc.id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${doc.slug}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Failed to download document:", error);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this document?")) return;

    try {
      await documentsApi.delete(id);
      fetchDocuments();
    } catch (error) {
      console.error("Failed to delete document:", error);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Documents</h1>
        <Link
          href="/generate"
          className="px-4 py-2 bg-brand-primary text-white rounded-md hover:bg-brand-primary-light"
        >
          Generate New
        </Link>
      </div>

      <div className="mb-4 flex items-center gap-4">
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="px-3 py-2 border rounded-md"
        >
          <option value="">All Status</option>
          <option value="draft">Draft</option>
          <option value="generating">Generating</option>
          <option value="ready">Ready</option>
          <option value="distributed">Distributed</option>
          <option value="failed">Failed</option>
        </select>
      </div>

      <div className="bg-white rounded-lg shadow-sm border">
        {loading ? (
          <div className="p-8 text-center text-gray-500">Loading...</div>
        ) : documents.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <p>No documents yet. Generate your first document to get started.</p>
          </div>
        ) : (
          <div className="divide-y">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="p-4 hover:bg-gray-50"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <h3 className="font-medium">{doc.title}</h3>
                      <span
                        className={`px-2 py-0.5 text-xs font-medium rounded-full ${
                          statusColors[doc.status]
                        }`}
                      >
                        {statusLabels[doc.status]}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 mt-1 line-clamp-1">
                      {doc.topic}
                    </p>
                    <div className="flex items-center gap-4 mt-2 text-xs text-gray-400">
                      <span>Created {formatDate(doc.created_at)}</span>
                      {doc.word_count && <span>{doc.word_count} words</span>}
                      {doc.statistics_count && (
                        <span>{doc.statistics_count} statistics</span>
                      )}
                      {doc.sources_count && <span>{doc.sources_count} sources</span>}
                    </div>
                  </div>
                  <div className="flex items-center gap-2 ml-4">
                    {doc.status === "ready" && doc.pdf_url && (
                      <button
                        onClick={() => handleDownload(doc)}
                        className="px-3 py-1.5 text-sm text-brand-primary hover:bg-brand-primary/10 rounded-md"
                      >
                        Download
                      </button>
                    )}
                    {doc.status === "generating" && (
                      <span className="px-3 py-1.5 text-sm text-blue-600">
                        Processing...
                      </span>
                    )}
                    {doc.status === "failed" && (
                      <Link
                        href={`/generate?retry=${doc.id}`}
                        className="px-3 py-1.5 text-sm text-orange-600 hover:bg-orange-50 rounded-md"
                      >
                        Retry
                      </Link>
                    )}
                    <button
                      onClick={() => handleDelete(doc.id)}
                      className="px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 rounded-md"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
