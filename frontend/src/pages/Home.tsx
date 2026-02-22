import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { HeroSection } from '../components/HeroSection'
import { ProjectCard } from '../components/ProjectCard'
import type { ProjectCardProps } from '../components/ProjectCard'
import { useDocumentTitle } from '../hooks/useDocumentTitle'

const skills = [
  { category: 'AI/ML', items: ['PyTorch', 'TensorFlow', 'ONNX', 'Hugging Face', 'scikit-learn'] },
  { category: 'Languages', items: ['Python', 'TypeScript', 'SQL', 'Bash'] },
  { category: 'Backend', items: ['FastAPI', 'SQLAlchemy', 'PostgreSQL', 'Redis'] },
  { category: 'Frontend', items: ['React', 'Tailwind CSS', 'Vite'] },
  { category: 'DevOps', items: ['Docker', 'Nginx', 'systemd', 'Cloudflare', 'Git'] },
  { category: 'Domain', items: ['Neuroscience', 'EEG/BCI', 'Signal Processing', 'Medical NLP'] },
]

export function Home() {
  useDocumentTitle('Home')

  const [featured, setFeatured] = useState<ProjectCardProps[]>([])

  useEffect(() => {
    fetch('/api/projects')
      .then((res) => res.json())
      .then((data: ProjectCardProps[]) => setFeatured(data.filter((p) => p.tier === 1)))
      .catch(() => {})
  }, [])

  return (
    <>
      <HeroSection />

      {/* Skills */}
      <section className="py-16">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-2xl font-bold font-display text-text-primary text-center">
            Skills &amp; Technologies
          </h2>
          <div className="mt-10 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
            {skills.map((group) => (
              <div key={group.category}>
                <h3 className="text-sm font-semibold text-text-muted uppercase tracking-wide">
                  {group.category}
                </h3>
                <div className="mt-3 flex flex-wrap gap-2">
                  {group.items.map((item) => (
                    <span
                      key={item}
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-bg-tertiary border border-border text-text-secondary"
                    >
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Projects */}
      {featured.length > 0 && (
        <section className="py-16 border-t border-border">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold font-display text-text-primary">
                Featured Projects
              </h2>
              <Link
                to="/projects"
                className="text-sm font-medium text-accent hover:text-accent-hover transition-colors"
              >
                View all &rarr;
              </Link>
            </div>
            <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
              {featured.map((project) => (
                <ProjectCard key={project.slug} {...project} />
              ))}
            </div>
          </div>
        </section>
      )}
    </>
  )
}
