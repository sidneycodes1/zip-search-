'use client'

import { useState } from 'react'
import { useSearch } from '../hooks/useSearch'
import { PhotoUpload } from './PhotoUpload'
import { SearchButton } from './SearchButton'

export function SearchForm() {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [photo, setPhoto] = useState<File | null>(null)
  const { loading, error, onSubmit } = useSearch()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    await onSubmit({ name, description, photo })
  }

  return (
    <form onSubmit={handleSubmit} className="w-full space-y-6">
      <div>
        <label className="block text-sm font-medium text-zip-text mb-2">
          Full name <span className="text-zip-error">*</span>
        </label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Full name"
          className="w-full px-4 py-3 bg-transparent border border-zip-border rounded text-zip-text placeholder:text-zip-muted placeholder:font-mono focus:outline-none focus:border-zip-accent focus:ring-1 focus:ring-zip-accent transition-colors"
          required
          minLength={2} 
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-zip-text mb-2">
          Brief description (optional)
        </label>
        <input
          type="text"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Brief description — e.g. VP Marketing at Opay Nigeria"
          className="w-full px-4 py-3 bg-transparent border border-zip-border rounded text-zip-text placeholder:text-zip-muted focus:outline-none focus:border-zip-accent focus:ring-1 focus:ring-zip-accent transition-colors"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-zip-text mb-2">
          Photo (optional)
        </label>
        <PhotoUpload onPhotoSelect={setPhoto} photo={photo} />
      </div>

      <div className="pt-2">
        <SearchButton loading={loading} />
      </div>

      {error && (
        <p className="text-zip-error text-sm font-mono mt-2">{error}</p>
      )}
    </form>
  )
}
