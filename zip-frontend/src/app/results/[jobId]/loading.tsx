import { SkeletonCard } from '@/features/results/components/SkeletonCard'

export default function Loading() {
  return (
    <div className="space-y-4">
      <SkeletonCard />
      <SkeletonCard />
      <SkeletonCard />
    </div>
  )
}
