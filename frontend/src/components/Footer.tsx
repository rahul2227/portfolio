export function Footer() {
  return (
    <footer className="border-t border-border py-8 mt-16">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row justify-between items-center gap-4">
        <p className="text-sm text-text-muted">
          &copy; {new Date().getFullYear()} Rahul Sharma. All rights reserved.
        </p>
        <div className="flex items-center gap-2 text-sm text-text-muted">
          <span>Powered by</span>
          <span className="inline-flex items-center gap-1 px-2 py-1 bg-live/10 text-live rounded-full text-xs font-medium">
            <svg className="w-2 h-2 animate-pulse-dot" viewBox="0 0 8 8" fill="currentColor">
              <circle cx="4" cy="4" r="4" />
            </svg>
            Raspberry Pi 4
          </span>
        </div>
      </div>
    </footer>
  )
}
