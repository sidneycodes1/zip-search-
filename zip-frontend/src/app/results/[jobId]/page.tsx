'use client'

import { Suspense } from 'react'
import { ResultsDashboard } from '@/features/results/components/ResultsDashboard'
import { SkeletonCard } from '@/features/results/components/SkeletonCard'

export default function ResultsPage({
  params,
}: {
  params: { jobId: string }
}) {
  return (
    <Suspense fallback={<SkeletonCard />}>
      <ResultsDashboard jobId={params.jobId} />
    </Suspense>
  )
}
