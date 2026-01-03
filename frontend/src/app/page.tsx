export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-brand-primary mb-4">
          Paper by aiConnected
        </h1>
        <p className="text-lg text-muted-foreground mb-8">
          Professional thought leadership content generation platform
        </p>
        <div className="flex gap-4 justify-center">
          <a
            href="/login"
            className="px-6 py-3 bg-brand-primary text-white rounded-md hover:bg-brand-primary-light transition-colors"
          >
            Sign In
          </a>
          <a
            href="/register"
            className="px-6 py-3 border border-brand-primary text-brand-primary rounded-md hover:bg-brand-primary/5 transition-colors"
          >
            Get Started
          </a>
        </div>
      </div>
    </main>
  );
}
