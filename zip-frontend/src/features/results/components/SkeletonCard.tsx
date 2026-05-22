'use client'

export function SkeletonCard() {
  return (
    <div className="bg-zip-surface border border-zip-border rounded p-4 flex gap-4 animate-pulse">
      {/* Thumbnail skeleton */}
      <div className="w-[60px] h-[60px] rounded bg-zip-border flex-shrink-0" />
      
      {/* Content skeleton */}
      <div className="flex-1 space-y-3 py-1">
        <div className="h-4 bg-zip-border rounded w-3/4" />
        <div className="h-3 bg-zip-border rounded w-1/4" />
        <div className="space-y-2 pt-1">
          <div className="h-3 bg-zip-border rounded w-full" />
          <div className="h-3 bg-zip-border rounded w-5/6" />
        </div>
      </div>
    </div>
  )
}
