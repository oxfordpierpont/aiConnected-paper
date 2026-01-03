export default function DashboardPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Stat Cards */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="text-sm text-muted-foreground">Total Clients</div>
          <div className="text-3xl font-bold mt-2">0</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="text-sm text-muted-foreground">Documents</div>
          <div className="text-3xl font-bold mt-2">0</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="text-sm text-muted-foreground">Scheduled</div>
          <div className="text-3xl font-bold mt-2">0</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="text-sm text-muted-foreground">Generating</div>
          <div className="text-3xl font-bold mt-2">0</div>
        </div>
      </div>
    </div>
  );
}
