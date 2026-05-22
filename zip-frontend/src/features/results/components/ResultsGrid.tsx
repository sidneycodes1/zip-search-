'use client'

import { ResultCard } from './ResultCard'
import type { SearchResult } from '../types'

interface ResultsGridProps {
  results: SearchResult[]
}

export function ResultsGrid({ results }: ResultsGridProps) {
  // Sort by face_matched first, then relevance_score
  const sortedResults = [...results].sort((a, b) => {
    if (a.face_matched === true && b.face_matched !== true) return -1;
    if (b.face_matched === true && a.face_matched !== true) return 1;
    return (b.relevance_score || 0) - (a.relevance_score || 0);
  });

  return (
    <div className="flex flex-col gap-3">
      {sortedResults.map((result, index) => (
        <ResultCard key={`${result.url}-${index}`} result={result} />
      ))}
    </div>
  )
}
