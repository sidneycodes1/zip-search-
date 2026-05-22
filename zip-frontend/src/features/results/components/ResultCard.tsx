'use client'

import type { SearchResult } from '../types'

interface ResultCardProps {
  result: SearchResult
}

export function ResultCard({ result }: ResultCardProps) {
  return (
    <a
      href={result.url}
      target="_blank"
      rel="noopener noreferrer"
      className="block relative bg-zip-surface border border-zip-border rounded p-4 hover:border-[#444444] hover:bg-[#1A1A1A] transition-colors group"
    >
      <div className="flex gap-4">
        {/* Left: Thumbnail & Badges */}
        <div className="flex flex-col items-center gap-2 flex-shrink-0">
          <div className="relative w-[60px] h-[60px] rounded overflow-hidden bg-zip-border">
            {result.thumbnail ? (
              <img src={result.thumbnail} alt={result.title} className="w-full h-full object-cover" />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-zip-muted text-xs">
                No img
              </div>
            )}
          </div>
          
          {/* Face match badge */}
          {result.face_matched === true && (
            <div className="flex items-center gap-1 text-[10px] text-zip-success font-mono">
              <span className="w-1.5 h-1.5 rounded-full bg-zip-success" />
              Verified
            </div>
          )}
          {result.face_matched === false && (
            <div className="flex items-center gap-1 text-[10px] text-zip-muted font-mono">
              <span className="w-1.5 h-1.5 rounded-full bg-zip-muted" />
              Unverified
            </div>
          )}
        </div>

        {/* Right: Content */}
        <div className="flex-1 min-w-0 pr-6">
          <h3 className="font-bold text-[14px] text-zip-text leading-tight mb-1 line-clamp-2">
            {result.title}
          </h3>
          
          <div className="flex items-center gap-2 text-[12px] text-zip-muted mb-2 font-mono">
            <span>{result.source}</span>
            {result.published_date && (
              <>
                <span>•</span>
                <span>{result.published_date}</span>
              </>
            )}
          </div>
          
          {result.summary && (
            <p className="text-[13px] text-zip-muted line-clamp-2 leading-snug">
              {result.summary}
            </p>
          )}
        </div>
      </div>

      {/* External link icon */}
      <div className="absolute top-4 right-4 text-zip-muted group-hover:text-zip-text transition-colors">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
          <polyline points="15 3 21 3 21 9"></polyline>
          <line x1="10" y1="14" x2="21" y2="3"></line>
        </svg>
      </div>
    </a>
  )
}
