import { useState } from 'react'

interface FormData {
  name: string
  email: string
  message: string
}

export function ContactForm() {
  const [formData, setFormData] = useState<FormData>({ name: '', email: '', message: '' })
  const [status, setStatus] = useState<'idle' | 'submitting' | 'success' | 'error'>('idle')
  const [errorMessage, setErrorMessage] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setStatus('submitting')
    setErrorMessage('')

    try {
      const res = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      })

      if (!res.ok) {
        const data = await res.json().catch(() => null)
        throw new Error(data?.detail || `Request failed with status ${res.status}`)
      }

      setStatus('success')
      setFormData({ name: '', email: '', message: '' })
    } catch (err) {
      setStatus('error')
      setErrorMessage(err instanceof Error ? err.message : 'Something went wrong')
    }
  }

  if (status === 'success') {
    return (
      <div className="bg-success/10 border border-success/20 rounded-lg p-6 text-center">
        <p className="text-success font-medium">Message sent successfully!</p>
        <button
          type="button"
          onClick={() => setStatus('idle')}
          className="mt-4 text-sm text-success/80 underline hover:text-success"
        >
          Send another message
        </button>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-text-secondary">
          Name
        </label>
        <input
          type="text"
          id="name"
          required
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          className="mt-1 block w-full rounded-lg border bg-bg-secondary border-border px-4 py-3 text-text-primary placeholder-text-muted focus:border-accent focus:ring-1 focus:ring-accent/20"
          placeholder="Your name"
        />
      </div>

      <div>
        <label htmlFor="email" className="block text-sm font-medium text-text-secondary">
          Email
        </label>
        <input
          type="email"
          id="email"
          required
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          className="mt-1 block w-full rounded-lg border bg-bg-secondary border-border px-4 py-3 text-text-primary placeholder-text-muted focus:border-accent focus:ring-1 focus:ring-accent/20"
          placeholder="you@example.com"
        />
      </div>

      <div>
        <label htmlFor="message" className="block text-sm font-medium text-text-secondary">
          Message
        </label>
        <textarea
          id="message"
          required
          rows={5}
          value={formData.message}
          onChange={(e) => setFormData({ ...formData, message: e.target.value })}
          className="mt-1 block w-full rounded-lg border bg-bg-secondary border-border px-4 py-3 text-text-primary placeholder-text-muted focus:border-accent focus:ring-1 focus:ring-accent/20 resize-y"
          placeholder="What would you like to discuss?"
        />
      </div>

      {status === 'error' && (
        <p className="text-sm text-error" role="alert">{errorMessage}</p>
      )}

      <button
        type="submit"
        disabled={status === 'submitting'}
        className="w-full sm:w-auto px-6 py-3 bg-accent text-white font-medium rounded-lg hover:bg-accent-hover transition-colors disabled:bg-accent/50 disabled:opacity-50 disabled:cursor-not-allowed focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
      >
        {status === 'submitting' ? 'Sending...' : 'Send Message'}
      </button>
    </form>
  )
}
