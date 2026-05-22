'use client'

import { useEffect, useState } from 'react'
import type { JobStatus } from '../types'

interface SearchProgressProps {
  status: JobStatus | null
}

const SOURCES = [
  'Searching podcasts...',
  'Searching news...',
  'Searching YouTube...',
  'Searching social profiles...'
]

export function SearchProgress({ status }: SearchProgressProps) {
  const [visibleSources, setVisibleSources] = useState<number>(0)
  const progress = status?.progress || 0
  
  useEffect(() => {
    // Staggered reveal 150ms per line
    const timer = setInterval(() => {
      setVisibleSources((prev) => {
        if (prev < SOURCES.length) return prev + 1
        clearInterval(timer)
        return prev
      })
    }, 150)
    
    return () => clearInterval(timer)
  }, [])

  return (
    <div className="w-full">
      <div className="flex justify-between items-end mb-2">
        <h2 className="text-xl font-bold text-zip-text font-mono">Search progress</h2>
        <span className="text-xl font-bold font-mono">{progress}%</span>
      </div>
      
      <div className="h-4 bg-zip-surface border border-zip-border rounded w-full overflow-hidden mb-2">
        <div 
          className="h-full bg-zip-accent transition-all duration-500 ease-out" 
          style={{ width: `${progress}%` }} 
        />
      </div>
      
      {status?.job_id && (
        <p className="text-xs font-mono text-zip-muted mb-8">
          Job ID: {status.job_id}
        </p>
      )}
      
      <div className="space-y-3 font-mono text-sm border border-zip-border bg-zip-surface p-6 rounded">
        {SOURCES.map((source, idx) => {
          if (idx >= visibleSources) return null
          
          // Show checkmark if progress is past a certain point, or if done
          const isDone = progress >= ((idx + 1) * 25) || status?.status === 'complete'
          
          return (
            <div key={idx} className="flex items-center text-zip-text animate-in fade-in slide-in-from-bottom-2 duration-300">
              <span className={`w-2 h-2 rounded-full mr-3 ${isDone ? 'bg-zip-success' : 'bg-zip-accent animate-pulse'}`} />
              <span className="flex-1">{source}</span>
              {isDone && (
                <svg className="w-5 h-5 text-zip-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                </svg>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
