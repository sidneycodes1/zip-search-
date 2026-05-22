'use client'

import { SearchForm } from '@/features/search/components/SearchForm'

export default function SearchPage() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-lg">
        <h1 className="text-5xl font-bold font-mono tracking-wider mb-2">ZIP</h1>
        <p className="text-zip-muted mb-8">Find anyone's public footprint.</p>
        
        <div className="bg-zip-surface border border-zip-border rounded-lg p-6">
          <SearchForm />
        </div>
        
        <p className="text-center text-zip-muted text-xs mt-6">
          Zip only finds publicly available information
        </p>
      </div>
    </main>
  )
}
