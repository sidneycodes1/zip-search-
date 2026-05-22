'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useJobPolling } from '../hooks/useJobPolling'
import { CategoryTabs } from './CategoryTabs'
import { ResultsGrid } from './ResultsGrid'
import { SearchProgress } from './SearchProgress'
import { EmptyState } from './EmptyState'
import { SkeletonCard } from './SkeletonCard'
import type { ResultCategory, SearchResult } from '../types'

interface ResultsDashboardProps {
  jobId: string
}

export function ResultsDashboard({ jobId }: ResultsDashboardProps) {
  const [activeCategory, setActiveCategory] = useState<ResultCategory>('podcast')
  const { status, loading, error } = useJobPolling(jobId)

  // Determine actual state
  const isFailed = status?.status === 'failed' || error
  const isRunning = status?.status === 'pending' || status?.status === 'running' || loading
  const isComplete = status?.status === 'complete'

  const results = status?.results?.results || []
  
  // Group results
  const groupedResults = results.reduce((acc, result) => {
    if (!acc[result.category]) {
      acc[result.category] = []
    }
    acc[result.category].push(result)
    return acc
  }, {} as Record<string, SearchResult[]>)

  const currentCategoryResults = groupedResults[activeCategory] || []

  // Header Component (shared across states)
  const Header = () => (
    <header className="flex items-center justify-between py-6 border-b border-zip-border mb-8">
      <Link href="/" className="text-3xl font-bold font-mono tracking-wider text-zip-text hover:text-zip-accent transition-colors">
        ZIP
      </Link>
      {status?.results?.query_name && (
        <span className="text-zip-muted font-mono text-sm">
          Results for {status.results.query_name}
        </span>
      )}
    </header>
  )

  if (isFailed) {
    return (
      <div className="min-h-screen flex flex-col p-4">
        <Header />
        <div className="flex-1 flex flex-col items-center justify-center">
          <div className="w-16 h-16 border-2 border-zip-error rounded-full flex items-center justify-center text-zip-error mb-4">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </div>
          <h2 className="text-xl text-zip-text font-bold mb-6">Search failed. Please try again.</h2>
          <Link href="/" className="bg-zip-accent text-black px-6 py-3 rounded font-bold hover:bg-[#D4E800] transition-colors">
            Back to Search
          </Link>
        </div>
      </div>
    )
  }

  if (isRunning || !status) {
    return (
      <div className="min-h-screen flex flex-col p-4 max-w-5xl mx-auto w-full">
        <Header />
        <div className="space-y-8">
          <SearchProgress status={status} />
          
          <div className="mt-12">
            <h3 className="text-sm font-mono text-zip-muted mb-4 uppercase tracking-widest">Gathering results...</h3>
            <div className="grid grid-cols-1 gap-4">
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Complete State
  return (
    <div className="min-h-screen flex flex-col p-4 max-w-5xl mx-auto w-full">
      <Header />
      
      <div className="mb-6">
        <p className="text-sm font-mono text-zip-muted">
          {status?.results?.total_results || 0} results found across {status?.results?.sources_searched?.length || 0} sources in {status?.results?.search_duration_seconds?.toFixed(1) || 0} seconds
        </p>
      </div>

      <CategoryTabs 
        activeCategory={activeCategory} 
        onChange={setActiveCategory} 
        groupedResults={groupedResults}
      />
      
      <div className="mt-6">
        {currentCategoryResults.length > 0 ? (
          <ResultsGrid results={currentCategoryResults} />
        ) : (
          <EmptyState category={activeCategory} />
        )}
      </div>
    </div>
  )
}
