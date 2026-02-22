import { useEffect, useState } from 'react'
import { ProjectCard } from '../components/ProjectCard'
import type { ProjectCardProps } from '../components/ProjectCard'
import { useDocumentTitle } from '../hooks/useDocumentTitle'

export function Projects() {
  useDocumentTitle('Projects')

  const [projects, setProjects] = useState<ProjectCardProps[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedTag, setSelectedTag] = useState<string | null>(null)

  useEffect(() => {
    fetch('/api/projects')
      .then((res) => {
        if (!res.ok) throw new Error(`Failed to load projects (${res.status})`)
        return res.json()
      })
      .then((data: ProjectCardProps[]) => {
        setProjects(data)
        setLoading(false)
      })
      .catch((err: Error) => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  const allTags = [...new Set(projects.flatMap((p) => p.tags))]
  const filtered = selectedTag
    ? projects.filter((p) => p.tags.includes(selectedTag))
    : projects

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-20 text-center">
        <p className="text-text-muted">Loading projects...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-20 text-center">
        <p className="text-error">{error}</p>
      </div>
    )
  }

  return (
    <section className="py-16">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold font-display text-text-primary">Projects</h1>
        <p className="mt-2 text-text-secondary">AI/ML projects and tools I&apos;ve built.</p>

        {/* Tag filter */}
        <div className="mt-8 flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => setSelectedTag(null)}
            className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
              selectedTag === null
                ? 'bg-accent text-white'
                : 'bg-bg-secondary text-text-secondary border border-border hover:bg-bg-tertiary'
            }`}
          >
            All
          </button>
          {allTags.map((tag) => (
            <button
              type="button"
              key={tag}
              onClick={() => setSelectedTag(tag)}
              className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                selectedTag === tag
                  ? 'bg-accent text-white'
                  : 'bg-bg-secondary text-text-secondary border border-border hover:bg-bg-tertiary'
              }`}
            >
              {tag}
            </button>
          ))}
        </div>

        {/* Project grid */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          {filtered.map((project) => (
            <ProjectCard key={project.slug} {...project} />
          ))}
        </div>
      </div>
    </section>
  )
}
