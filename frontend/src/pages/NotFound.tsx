import { Link } from 'react-router-dom'
import { useDocumentTitle } from '../hooks/useDocumentTitle'

export function NotFound() {
  useDocumentTitle('Page Not Found')

  return (
    <section className="py-20 text-center">
      <div className="max-w-2xl mx-auto px-4">
        <h1 className="text-8xl font-bold font-display text-accent/30">404</h1>
        <p className="mt-4 text-xl text-text-secondary">
          This page doesn&apos;t exist.
        </p>
        <Link
          to="/"
          className="mt-8 inline-flex items-center justify-center px-6 py-3 bg-accent text-white font-medium rounded-lg hover:bg-accent-hover transition-colors"
        >
          Go Home
        </Link>
      </div>
    </section>
  )
}
