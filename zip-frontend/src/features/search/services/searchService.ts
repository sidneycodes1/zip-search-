import { api } from '@/lib/api'
import type { SearchFormData } from '../types'

interface SearchResponse {
  job_id: string
}

export const searchService = {
  async search(data: SearchFormData): Promise<SearchResponse> {
    const formData = new FormData()
    formData.append('name', data.name)
    formData.append('description', data.description)
    if (data.photo) {
      formData.append('photo', data.photo)
    }

    const response = await api.post<SearchResponse>('/api/v1/search', formData, {
      // Don't set Content-Type header manually for FormData, let the browser set it with the boundary
    })

    return response
  },
}
