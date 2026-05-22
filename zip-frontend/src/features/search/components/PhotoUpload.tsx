'use client'

import { useState, useEffect } from 'react'

interface PhotoUploadProps {
  onPhotoSelect: (file: File | null) => void
  photo?: File | null
}

export function PhotoUpload({ onPhotoSelect, photo }: PhotoUploadProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [preview, setPreview] = useState<string | null>(null)

  useEffect(() => {
    if (!photo) {
      setPreview(null)
    }
  }, [photo])

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file && file.type.startsWith('image/')) {
      onPhotoSelect(file)
      const reader = new FileReader()
      reader.onload = (e) => setPreview(e.target?.result as string)
      reader.readAsDataURL(file)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      onPhotoSelect(file)
      const reader = new FileReader()
      reader.onload = (e) => setPreview(e.target?.result as string)
      reader.readAsDataURL(file)
    }
  }

  const handleRemove = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    onPhotoSelect(null)
    setPreview(null)
  }

  return (
    <div
      onDrop={handleDrop}
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
      onDragLeave={() => setIsDragging(false)}
      className={`border border-dashed rounded p-6 text-center transition-colors relative ${
        isDragging ? 'border-zip-accent bg-zip-surface/80' : 'border-zip-border bg-transparent hover:border-zip-muted'
      }`}
    >
      {preview ? (
        <div className="relative inline-block">
          <img src={preview} alt="Preview" className="w-16 h-16 object-cover mx-auto rounded" />
          <button
            onClick={handleRemove}
            className="absolute -top-2 -right-2 bg-zip-surface border border-zip-border rounded-full w-6 h-6 flex items-center justify-center text-zip-muted hover:text-zip-text hover:border-zip-muted transition-colors"
            title="Remove photo"
          >
            ×
          </button>
        </div>
      ) : (
        <label htmlFor="photo-upload" className="cursor-pointer flex flex-col items-center justify-center h-full w-full">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-zip-muted mb-2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="17 8 12 3 7 8"></polyline>
            <line x1="12" y1="3" x2="12" y2="15"></line>
          </svg>
          <span className="text-sm text-zip-muted font-mono">
            Drop a photo or <span className="underline decoration-zip-muted underline-offset-2">click to upload</span>
          </span>
          <span className="text-xs text-zip-muted mt-1 opacity-50">PNG, JPG up to 10MB</span>
          <input
            type="file"
            accept="image/*"
            onChange={handleChange}
            className="hidden"
            id="photo-upload"
          />
        </label>
      )}
    </div>
  )
}
