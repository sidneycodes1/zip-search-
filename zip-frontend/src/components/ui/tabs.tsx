'use client'

import React, { useState } from 'react'

interface TabsProps {
  defaultValue?: string
  children: React.ReactNode
}

interface TabsContextType {
  activeTab: string
  setActiveTab: (value: string) => void
}

const TabsContext = React.createContext<TabsContextType | undefined>(undefined)

export const Tabs = ({ defaultValue = '', children }: TabsProps) => {
  const [activeTab, setActiveTab] = useState(defaultValue)

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div>{children}</div>
    </TabsContext.Provider>
  )
}

interface TabsListProps {
  children: React.ReactNode
}

export const TabsList = ({ children }: TabsListProps) => (
  <div className="flex gap-4 border-b border-gray-200">{children}</div>
)

interface TabsTriggerProps {
  value: string
  children: React.ReactNode
}

export const TabsTrigger = ({ value, children }: TabsTriggerProps) => {
  const context = React.useContext(TabsContext)
  if (!context) throw new Error('TabsTrigger must be used within Tabs')

  return (
    <button
      onClick={() => context.setActiveTab(value)}
      className={`px-4 py-2 font-medium transition ${
        context.activeTab === value
          ? 'text-black border-b-2 border-black'
          : 'text-gray-600 hover:text-black'
      }`}
    >
      {children}
    </button>
  )
}

interface TabsContentProps {
  value: string
  children: React.ReactNode
}

export const TabsContent = ({ value, children }: TabsContentProps) => {
  const context = React.useContext(TabsContext)
  if (!context) throw new Error('TabsContent must be used within Tabs')

  return context.activeTab === value ? <>{children}</> : null
}
