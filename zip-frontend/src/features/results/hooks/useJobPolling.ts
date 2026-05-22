'use client'

import { useState, useEffect } from 'react'
import { jobService } from '../services/jobService'
import type { JobStatus } from '../types'

export function useJobPolling(jobId: string) {
  const [status, setStatus] = useState<JobStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let intervalId: NodeJS.Timeout

    const poll = async () => {
      try {
        const response = await jobService.getStatus(jobId)
        setStatus(response)

        // Stop polling if job is complete or failed
        if (response.status === 'complete' || response.status === 'failed') {
          setLoading(false)
          clearInterval(intervalId)
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch status')
        setLoading(false)
        clearInterval(intervalId)
      }
    }

    poll()
    intervalId = setInterval(poll, 2000)

    return () => clearInterval(intervalId)
  }, [jobId])

  return { status, loading, error }
}
