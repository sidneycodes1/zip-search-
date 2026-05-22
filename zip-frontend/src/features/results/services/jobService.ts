import { api } from '@/lib/api'
import type { JobStatus } from '../types'

export const jobService = {
  async getStatus(jobId: string): Promise<JobStatus> {
    const response = await api.get<JobStatus>(`/api/v1/search/status/${jobId}`)
    return response
  },
}
