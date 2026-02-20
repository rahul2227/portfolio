import { ContactForm } from '../components/ContactForm'

export function Contact() {
  return (
    <section className="py-16">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-gray-900">Get in Touch</h1>
        <p className="mt-2 text-gray-600">
          Have a question or want to collaborate? Send me a message.
        </p>

        <div className="mt-10">
          <ContactForm />
        </div>
      </div>
    </section>
  )
}
