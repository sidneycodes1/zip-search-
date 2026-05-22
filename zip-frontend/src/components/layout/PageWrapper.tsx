'use client'

import { ReactNode } from 'react'
import { Header } from './Header'

interface PageWrapperProps {
  children: ReactNode
}

export function PageWrapper({ children }: PageWrapperProps) {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 container py-8">{children}</main>
    </div>
  )
}
