'use client'

import type { ResultCategory, SearchResult } from '../types'

interface CategoryTabsProps {
  activeCategory: ResultCategory
  onChange: (category: ResultCategory) => void
  groupedResults: Record<string, SearchResult[]>
}

const CATEGORIES: { value: ResultCategory; label: string }[] = [
  { value: 'podcast', label: 'Podcasts' },
  { value: 'news', label: 'News' },
  { value: 'video', label: 'Videos' },
  { value: 'social', label: 'Social' },
]

export function CategoryTabs({ activeCategory, onChange, groupedResults }: CategoryTabsProps) {
  return (
    <div className="flex gap-8 border-b border-zip-border font-mono text-sm w-full">
      {CATEGORIES.map(({ value, label }) => {
        const count = groupedResults[value]?.length || 0
        const isActive = activeCategory === value
        
        return (
          <button
            key={value}
            onClick={() => onChange(value)}
            className={`pb-3 relative transition-colors ${
              isActive
                ? 'text-zip-text'
                : 'text-zip-muted hover:text-zip-text'
            }`}
          >
            {label} ({count})
            {isActive && (
              <span className="absolute bottom-0 left-0 w-full h-[2px] bg-zip-accent" />
            )}
          </button>
        )
      })}
    </div>
  )
}
