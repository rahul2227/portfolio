import { ContactForm } from '../components/ContactForm'
import { useDocumentTitle } from '../hooks/useDocumentTitle'

export function Contact() {
  useDocumentTitle('Contact')

  return (
    <section className="py-16">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold font-display text-text-primary">Get in Touch</h1>
        <p className="mt-2 text-text-secondary">
          Have a question or want to collaborate? Send me a message.
        </p>

        <div className="mt-10">
          <ContactForm />
        </div>
      </div>
    </section>
  )
}
