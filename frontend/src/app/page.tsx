export default function Home() {
  return (
    <div className="flex min-h-screen flex-col bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b border-slate-200/80 bg-white/80 backdrop-blur-md">
        <div className="container mx-auto flex h-16 items-center justify-between px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-600 to-blue-600">
              <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h1 className="text-xl font-semibold tracking-tight text-slate-900">
              Resume AI Agent
            </h1>
          </div>
          
          {/* Placeholder for dark mode toggle */}
          <div className="flex items-center gap-4">
            <div className="h-9 w-9 rounded-lg border border-slate-200 bg-slate-50"></div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="container mx-auto flex flex-1 flex-col gap-6 p-6">
        <div className="flex flex-1 flex-col gap-6 lg:flex-row">
          {/* Left Sidebar - Upload Section */}
          <aside className="flex flex-col gap-4 lg:w-80">
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="mb-4 text-lg font-semibold text-slate-900">
                Upload Resume
              </h2>
              
              {/* PDF Upload Placeholder */}
              <div className="flex h-40 flex-col items-center justify-center rounded-lg border-2 border-dashed border-slate-300 bg-slate-50 p-6 text-center transition-colors hover:border-indigo-400 hover:bg-indigo-50/50">
                <svg className="mb-3 h-10 w-10 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p className="text-sm font-medium text-slate-600">
                  Drop PDF here or click to browse
                </p>
                <p className="mt-1 text-xs text-slate-500">
                  Max file size: 10MB
                </p>
              </div>
            </div>

            {/* Instructions Card */}
            <div className="rounded-xl border border-indigo-200 bg-gradient-to-br from-indigo-50 to-blue-50 p-5">
              <h3 className="mb-2 text-sm font-semibold text-indigo-900">
                How it works
              </h3>
              <ol className="space-y-2 text-sm text-slate-700">
                <li className="flex gap-2">
                  <span className="font-semibold text-indigo-600">1.</span>
                  <span>Upload your resume PDF</span>
                </li>
                <li className="flex gap-2">
                  <span className="font-semibold text-indigo-600">2.</span>
                  <span>Paste job description or URL</span>
                </li>
                <li className="flex gap-2">
                  <span className="font-semibold text-indigo-600">3.</span>
                  <span>Review AI suggestions</span>
                </li>
                <li className="flex gap-2">
                  <span className="font-semibold text-indigo-600">4.</span>
                  <span>Download optimized resume</span>
                </li>
              </ol>
            </div>
          </aside>
        </div>
      </main>
    </div>
  );
}
