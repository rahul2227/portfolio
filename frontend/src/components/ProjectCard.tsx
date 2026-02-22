import { Link } from 'react-router-dom'

export interface ProjectCardProps {
  slug: string
  title: string
  description: string
  tags: string[]
  tier: number
  github_url: string | null
  demo_url: string | null
}

export function ProjectCard({ slug, title, description, tags, tier, github_url, demo_url }: ProjectCardProps) {
  return (
    <Link to={`/projects/${slug}`} className="block group">
      <article className="rounded-lg border border-border bg-bg-secondary p-6 transition-all duration-300 hover:border-accent/50 hover:shadow-[0_0_20px_var(--color-accent-glow)] hover:scale-[1.02]">
        <div className="flex items-start justify-between gap-3">
          <h3 className="text-lg font-semibold font-display text-text-primary group-hover:text-accent transition-colors">
            {title}
          </h3>
          {demo_url && tier === 1 ? (
            <span className="inline-flex items-center gap-1.5 px-2 py-0.5 bg-live/10 text-live rounded-full text-xs font-medium shrink-0">
              <svg className="w-1.5 h-1.5 animate-pulse-dot" viewBox="0 0 6 6" fill="currentColor">
                <circle cx="3" cy="3" r="3" />
              </svg>
              Live Demo
            </span>
          ) : demo_url && (
            <span className="inline-flex items-center gap-1.5 px-2 py-0.5 bg-error/10 text-error rounded-full text-xs font-medium shrink-0">
              <svg className="w-1.5 h-1.5" viewBox="0 0 6 6" fill="currentColor">
                <circle cx="3" cy="3" r="3" />
              </svg>
              Demo
            </span>
          )}
        </div>
        <p className="mt-2 text-sm text-text-secondary line-clamp-3">
          {description}
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          {tags.map((tag) => (
            <span
              key={tag}
              className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-tag/10 text-tag border border-tag/20"
            >
              {tag}
            </span>
          ))}
        </div>
        {(github_url || demo_url) && (
          <div className="mt-4 flex gap-4">
            {github_url && (
              <a
                href={github_url}
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => e.stopPropagation()}
                className="text-sm font-medium text-text-secondary hover:text-text-primary transition-colors"
              >
                GitHub
              </a>
            )}
            {demo_url && (
              <a
                href={demo_url}
                onClick={(e) => e.stopPropagation()}
                className="text-sm font-medium text-accent hover:text-accent-hover transition-colors"
              >
                Try Demo
              </a>
            )}
          </div>
        )}
      </article>
    </Link>
  )
}
