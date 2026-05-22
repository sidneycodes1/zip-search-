export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
export const POLL_INTERVAL = 2000 // 2 seconds

export const CATEGORIES = [
  'podcasts',
  'news',
  'videos',
  'social',
] as const

export const CATEGORY_LABELS: Record<string, string> = {
  podcasts: 'Podcasts',
  news: 'News',
  videos: 'Videos',
  social: 'Social Media',
}
