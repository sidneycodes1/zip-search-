'use client'

import type { ResultCategory } from '../types'

interface EmptyStateProps {
  category: ResultCategory
}

export function EmptyState({ category }: EmptyStateProps) {
  const categoryName = category.charAt(0).toUpperCase() + category.slice(1)

  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <div className="w-16 h-16 mb-4 text-zip-muted opacity-50">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="w-full h-full">
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="16" y1="2" x2="16" y2="6"></line>
          <line x1="8" y1="2" x2="8" y2="6"></line>
          <line x1="3" y1="10" x2="21" y2="10"></line>
          <path d="M8 14h.01"></path>
          <path d="M12 14h.01"></path>
          <path d="M16 14h.01"></path>
          <path d="M8 18h.01"></path>
          <path d="M12 18h.01"></path>
          <path d="M16 18h.01"></path>
        </svg>
      </div>
      <p className="text-zip-text text-lg font-mono mb-2">Nothing found on {categoryName}</p>
      <p className="text-zip-muted text-sm font-mono">We couldn't find any public results in this category.</p>
    </div>
  )
}
