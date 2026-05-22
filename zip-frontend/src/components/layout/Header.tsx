'use client'

import Link from 'next/link'
import { WalletButton } from './WalletButton'

export function Header() {
  return (
    <header className="border-b border-gray-200 py-4">
      <div className="container flex items-center justify-between">
        <Link href="/" className="text-2xl font-bold font-mono">
          Zip
        </Link>
        <nav className="flex items-center gap-6">
          <a href="/" className="text-gray-600 hover:text-black transition">
            Search
          </a>
          <a href="#" className="text-gray-600 hover:text-black transition">
            About
          </a>
          <div className="ml-4 pl-4 border-l border-gray-200">
            <WalletButton />
          </div>
        </nav>
      </div>
    </header>
  )
}
