import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useDocumentTitle } from '../hooks/useDocumentTitle'

interface ProjectDetail {
  id: number
  slug: string
  title: string
  description: string
  long_description: string | null
  tags: string[]
  tier: number
  order: number
  github_url: string | null
  demo_url: string | null
  image_url: string | null
}

export function ProjectDetail() {
  const { slug } = useParams<{ slug: string }>()
  const [project, setProject] = useState<ProjectDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [notFound, setNotFound] = useState(false)
  const [error, setError] = useState('')

  useDocumentTitle(project?.title ?? '')

  useEffect(() => {
    fetch(`/api/projects/${slug}`)
      .then((res) => {
        if (res.status === 404) {
          setNotFound(true)
          setLoading(false)
          return null
        }
        if (!res.ok) throw new Error(`Failed to load project (${res.status})`)
        return res.json()
      })
      .then((data: ProjectDetail | null) => {
        if (data) {
          setProject(data)
          setLoading(false)
        }
      })
      .catch((err: Error) => {
        setError(err.message)
        setLoading(false)
      })
  }, [slug])

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center">
        <p className="text-text-muted">Loading project...</p>
      </div>
    )
  }

  if (notFound) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center">
        <h1 className="text-4xl font-bold font-display text-text-primary">Project Not Found</h1>
        <p className="mt-4 text-text-secondary">The project you're looking for doesn't exist.</p>
        <Link to="/projects" className="mt-6 inline-block text-accent hover:text-accent-hover">
          &larr; Back to Projects
        </Link>
      </div>
    )
  }

  if (error || !project) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center">
        <p className="text-error">{error || 'Something went wrong'}</p>
      </div>
    )
  }

  return (
    <section className="py-16">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Back link */}
        <Link to="/projects" className="text-sm text-text-secondary hover:text-accent transition-colors">
          &larr; Back to Projects
        </Link>

        {/* Header */}
        <h1 className="mt-6 text-3xl sm:text-4xl font-bold font-display text-text-primary">
          {project.title}
        </h1>

        {/* Tags */}
        <div className="mt-4 flex flex-wrap gap-2">
          {project.tags.map((tag) => (
            <span
              key={tag}
              className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-tag/10 text-tag border border-tag/20"
            >
              {tag}
            </span>
          ))}
        </div>

        {/* Action buttons */}
        <div className="mt-6 flex flex-wrap gap-3">
          {project.tier === 1 && project.demo_url && (
            <a
              href={project.demo_url}
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-accent text-white font-medium rounded-lg hover:bg-accent-hover transition-colors"
            >
              <svg className="w-1.5 h-1.5 animate-pulse-dot" viewBox="0 0 6 6" fill="currentColor">
                <circle cx="3" cy="3" r="3" />
              </svg>
              Try Live Demo
            </a>
          )}
          {project.github_url && (
            <a
              href={project.github_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center px-5 py-2.5 text-text-primary font-medium rounded-lg border border-border hover:bg-bg-tertiary transition-colors"
            >
              View Source
            </a>
          )}
        </div>

        {/* Description */}
        <div className="mt-10 space-y-4">
          <p className="text-text-secondary text-lg">{project.description}</p>

          {project.long_description && (
            <div className="mt-6 space-y-4 text-text-secondary leading-relaxed">
              {project.long_description.split('\n\n').map((paragraph, i) => (
                <p key={i}>{paragraph}</p>
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  )
}
