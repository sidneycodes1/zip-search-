export type ResultCategory = 'podcast' | 'news' | 'video' | 'social' | 'article' | 'other'

export interface SearchResult {
  title: string
  url: string
  source: string
  category: ResultCategory
  summary: string | null
  thumbnail: string | null
  published_date: string | null
  relevance_score: number
  face_matched: boolean | null
}

export interface JobResults {
  query_name: string
  query_description?: string
  total_results: number
  sources_searched: string[]
  search_duration_seconds: number
  job_id: string
  results: SearchResult[]
}

export interface JobStatus {
  job_id: string
  status: 'pending' | 'running' | 'complete' | 'failed'
  progress: number
  results: JobResults | null
  error: string | null
}
