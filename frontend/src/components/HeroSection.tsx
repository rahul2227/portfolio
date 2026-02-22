import { Link } from 'react-router-dom'

export function HeroSection() {
  return (
    <section className="py-20 sm:py-28">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h1
          className="text-4xl sm:text-5xl lg:text-6xl font-bold font-display tracking-tight text-text-primary animate-fade-up"
        >
          AI/ML Engineer
        </h1>
        <p
          className="mt-6 text-lg sm:text-xl text-text-secondary max-w-2xl mx-auto animate-fade-up"
          style={{ animationDelay: '0.1s' }}
        >
          Building intelligent systems at the intersection of artificial intelligence
          and neuroscience. Exploring generative models, NLP, and reinforcement learning.
        </p>
        <div
          className="mt-10 flex flex-col sm:flex-row gap-4 justify-center animate-fade-up"
          style={{ animationDelay: '0.2s' }}
        >
          <Link
            to="/projects"
            className="inline-flex items-center justify-center px-6 py-3 bg-accent text-white font-medium rounded-lg hover:bg-accent-hover transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            View Projects
          </Link>
          <Link
            to="/contact"
            className="inline-flex items-center justify-center px-6 py-3 text-text-primary font-medium rounded-lg border border-border hover:bg-bg-tertiary transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-border"
          >
            Get in Touch
          </Link>
        </div>
      </div>
    </section>
  )
}
