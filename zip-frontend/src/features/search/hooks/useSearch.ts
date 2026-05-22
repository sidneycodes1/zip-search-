'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { searchService } from '../services/searchService'
import type { SearchFormData } from '../types'

export function useSearch() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  const onSubmit = async (data: SearchFormData) => {
    setLoading(true)
    setError(null)

    try {
      const result = await searchService.search(data)
      // Redirect to results page with job ID
      router.push(`/results/${result.job_id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed')
      setLoading(false)
    }
  }

  return { loading, error, onSubmit }
}
