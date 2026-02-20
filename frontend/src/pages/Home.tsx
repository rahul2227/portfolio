import { HeroSection } from '../components/HeroSection'

const skills = [
  { category: 'AI/ML', items: ['PyTorch', 'TensorFlow', 'ONNX', 'Hugging Face', 'scikit-learn'] },
  { category: 'Languages', items: ['Python', 'TypeScript', 'SQL', 'Bash'] },
  { category: 'Backend', items: ['FastAPI', 'SQLAlchemy', 'PostgreSQL', 'Redis'] },
  { category: 'Frontend', items: ['React', 'Tailwind CSS', 'Vite'] },
  { category: 'DevOps', items: ['Docker', 'Nginx', 'systemd', 'Cloudflare', 'Git'] },
  { category: 'Domain', items: ['Neuroscience', 'EEG/BCI', 'Signal Processing', 'Medical NLP'] },
]

export function Home() {
  return (
    <>
      <HeroSection />

      <section className="py-16 bg-gray-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-2xl font-bold text-gray-900 text-center">Skills & Technologies</h2>
          <div className="mt-10 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
            {skills.map((group) => (
              <div key={group.category}>
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
                  {group.category}
                </h3>
                <div className="mt-3 flex flex-wrap gap-2">
                  {group.items.map((item) => (
                    <span
                      key={item}
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-white border border-gray-200 text-gray-700"
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
    </>
  )
}
