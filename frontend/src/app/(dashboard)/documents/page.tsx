export default function DocumentsPage() {
  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Documents</h1>
        <button className="px-4 py-2 bg-brand-primary text-white rounded-md hover:bg-brand-primary-light">
          Generate New
        </button>
      </div>
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-8 text-center text-muted-foreground">
          <p>No documents yet. Generate your first document to get started.</p>
        </div>
      </div>
    </div>
  );
}
