import { Routes, Route } from 'react-router-dom'
import { Navbar } from './components/Navbar'
import { Footer } from './components/Footer'
import { Home } from './pages/Home'
import { Projects } from './pages/Projects'
import { About } from './pages/About'
import { Contact } from './pages/Contact'
import { ProjectDetail } from './pages/ProjectDetail'
import { NotFound } from './pages/NotFound'

export function App() {
  return (
    <div className="min-h-screen flex flex-col bg-bg-primary text-text-primary">
      <Navbar />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/projects" element={<Projects />} />
          <Route path="/projects/:slug" element={<ProjectDetail />} />
          <Route path="/about" element={<About />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      <Footer />
    </div>
  )
}
