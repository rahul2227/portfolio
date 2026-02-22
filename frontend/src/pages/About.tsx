import { useDocumentTitle } from '../hooks/useDocumentTitle'

export function About() {
  useDocumentTitle('About')

  return (
    <section className="py-16">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold font-display text-text-primary">About Me</h1>

        <div className="mt-8 prose prose-invert max-w-none">
          <p className="text-lg text-text-secondary">
            I&apos;m an AI/ML engineer with a background in neuroscience, focused on building
            intelligent systems that bridge the gap between brain science and artificial intelligence.
          </p>

          <h2 className="text-xl font-semibold font-display text-text-primary mt-10">Background</h2>
          <p className="text-text-secondary">
            My work spans generative models for neural signal synthesis, natural language processing
            for medical research, computer vision, and reinforcement learning. I&apos;m passionate about
            deploying ML models on edge devices and making AI accessible.
          </p>

          <h2 className="text-xl font-semibold font-display text-text-primary mt-10">Technical Focus</h2>
          <ul className="mt-4 space-y-3 text-text-secondary">
            <li className="flex items-start gap-3">
              <span className="mt-1.5 w-1.5 h-1.5 bg-accent rounded-full flex-shrink-0" />
              <span>Generative AI — GANs, VAEs, and Diffusion models for EEG signal synthesis</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="mt-1.5 w-1.5 h-1.5 bg-accent rounded-full flex-shrink-0" />
              <span>NLP — RAG systems, medical chatbots, text extraction pipelines</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="mt-1.5 w-1.5 h-1.5 bg-accent rounded-full flex-shrink-0" />
              <span>Edge ML — Model optimization (ONNX, TFLite, INT8 quantization) for ARM</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="mt-1.5 w-1.5 h-1.5 bg-accent rounded-full flex-shrink-0" />
              <span>Reinforcement Learning — Game-playing agents with real-time visualization</span>
            </li>
          </ul>

          <h2 className="text-xl font-semibold font-display text-text-primary mt-10">This Site</h2>
          <p className="text-text-secondary">
            This portfolio is self-hosted on a Raspberry Pi 4 (4GB) — a $55 ARM computer running
            the full stack: React frontend, FastAPI backend, Nginx reverse proxy, and Cloudflare
            tunnel. Interactive ML demos run directly on the Pi using optimized models.
          </p>
        </div>
      </div>
    </section>
  )
}
