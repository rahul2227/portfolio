export interface ProjectCardProps {
  slug: string
  title: string
  description: string
  tags: string[]
  tier: number
  github_url: string | null
  demo_url: string | null
}

export function ProjectCard({ title, description, tags, github_url, demo_url }: ProjectCardProps) {
  return (
    <article className="group rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <h3 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
        {title}
      </h3>
      <p className="mt-2 text-sm text-gray-600 line-clamp-3">
        {description}
      </p>
      <div className="mt-4 flex flex-wrap gap-2">
        {tags.map((tag) => (
          <span
            key={tag}
            className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700"
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
              className="text-sm font-medium text-gray-600 hover:text-gray-900"
            >
              GitHub
            </a>
          )}
          {demo_url && (
            <a
              href={demo_url}
              className="text-sm font-medium text-blue-600 hover:text-blue-700"
            >
              Live Demo
            </a>
          )}
        </div>
      )}
    </article>
  )
}
