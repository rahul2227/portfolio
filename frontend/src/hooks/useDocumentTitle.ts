import { useEffect } from 'react'

export function useDocumentTitle(title: string): void {
  useEffect(() => {
    const base = 'Rahul Sharma | AI/ML Engineer'
    document.title = title ? `${title} | Rahul Sharma` : base
  }, [title])
}
