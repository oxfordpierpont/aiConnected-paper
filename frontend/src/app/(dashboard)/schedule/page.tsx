export default function SchedulePage() {
  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Schedule</h1>
        <div className="flex gap-2">
          <button className="px-4 py-2 border rounded-md hover:bg-gray-50">
            Import CSV
          </button>
          <button className="px-4 py-2 bg-brand-primary text-white rounded-md hover:bg-brand-primary-light">
            Schedule Content
          </button>
        </div>
      </div>
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-8 text-center text-muted-foreground">
          <p>No scheduled content. Schedule content to automate your publishing.</p>
        </div>
      </div>
    </div>
  );
}
