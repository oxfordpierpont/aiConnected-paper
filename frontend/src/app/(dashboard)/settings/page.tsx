export default function SettingsPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Settings</h1>
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="border-b pb-4 mb-4">
          <h2 className="text-lg font-semibold">General</h2>
          <p className="text-sm text-muted-foreground">Manage your agency settings</p>
        </div>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Agency Name</label>
            <input
              type="text"
              className="w-full max-w-md px-3 py-2 border rounded-md"
              placeholder="Your Agency"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Website</label>
            <input
              type="url"
              className="w-full max-w-md px-3 py-2 border rounded-md"
              placeholder="https://example.com"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
